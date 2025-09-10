from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Client, ClientProfile, ClientBlock
from .serializers import ClientSerializer, ClientBlockSerializer

from .services.profile_normalizer import normalize_client_profile
from .services.generator import generate_week_plan


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all().order_by("-created_at")
    serializer_class = ClientSerializer

    @action(detail=True, methods=["get"], url_path="plan")
    def plan(self, request, pk=None):
        client = get_object_or_404(Client, pk=pk)

        # Ensure we have a normalized profile
        profile_obj = getattr(client, "profile", None)
        if not profile_obj:
            data = normalize_client_profile(client)
            profile_obj = ClientProfile.objects.create(client=client, profile=data)
        profile = profile_obj.profile

        save = request.query_params.get("save") in ("1", "true", "True")
        plan = generate_week_plan(client, profile, save=save)
        if save:
            # Persist as a ClientBlock
            name = request.query_params.get("name") or f"Plan {client}"
            try:
                block = plan.get("plan") if isinstance(plan, dict) else None
                if block:
                    ClientBlock.objects.create(client=client, name=name, block=block)
            except Exception:
                pass
        return Response(plan, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="plan/save")
    def save_plan(self, request, pk=None):
        client = get_object_or_404(Client, pk=pk)
        name = (request.data or {}).get("name") or f"Plan {client}"
        block = (request.data or {}).get("plan") or (request.data or {}).get("block")
        if not isinstance(block, (dict, list)):
            return Response({"detail": "Provide plan or block JSON."}, status=status.HTTP_400_BAD_REQUEST)
        cb = ClientBlock.objects.create(client=client, name=name, block=block)
        return Response(ClientBlockSerializer(cb).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="blocks")
    def list_blocks(self, request, pk=None):
        client = get_object_or_404(Client, pk=pk)
        qs = client.blocks.all().order_by("-created_at")
        return Response(ClientBlockSerializer(qs, many=True).data)

    @action(detail=True, methods=["get", "patch", "delete"], url_path=r"blocks/(?P<block_id>[^/.]+)")
    def block_detail(self, request, pk=None, block_id=None):
        client = get_object_or_404(Client, pk=pk)
        block = get_object_or_404(ClientBlock, pk=block_id, client=client)
        if request.method == "GET":
            return Response(ClientBlockSerializer(block).data)
        if request.method == "PATCH":
            ser = ClientBlockSerializer(block, data=request.data, partial=True)
            ser.is_valid(raise_exception=True)
            ser.save()
            return Response(ser.data)
        # DELETE
        block.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path=r"blocks/(?P<block_id>[^/.]+)/export")
    def block_export(self, request, pk=None, block_id=None):
        import csv as _csv
        from io import StringIO
        client = get_object_or_404(Client, pk=pk)
        block = get_object_or_404(ClientBlock, pk=block_id, client=client)
        fmt = (request.query_params.get("format") or "csv").lower()
        name = (block.name or f"plan_{block.id}").replace(" ", "_")
        data = block.block or {}
        # Normalize to entries: [(day,title,exercise dict)]
        entries = []
        if isinstance(data, dict):
            for day, arr in data.items():
                if isinstance(arr, list):
                    for it in arr:
                        if isinstance(it, dict):
                            entries.append((day, it))
        elif isinstance(data, list):
            for i, arr in enumerate(data, start=1):
                day = f"Day {i}"
                if isinstance(arr, list):
                    for it in arr:
                        if isinstance(it, dict):
                            entries.append((day, it))

        if fmt == "html":
            rows = []
            for day, it in entries:
                title = it.get("name") or it.get("exercise") or "Exercise"
                mp = it.get("movement_pattern") or ""
                sets = it.get("sets") or ""
                reps = it.get("reps") or ""
                rest = it.get("rest_s") or it.get("rest") or ""
                notes = it.get("notes") or ""
                rows.append(f"<tr><td>{day}</td><td>{title}</td><td>{mp}</td><td>{sets}</td><td>{reps}</td><td>{rest}</td><td>{notes}</td></tr>")
            html = (
                f"<!doctype html><html><head><meta charset='utf-8'><title>{name}</title>"
                "<style>body{font-family:system-ui,Arial;padding:16px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #e5e7eb;padding:6px;font-size:12px}th{background:#f8fafc}</style>" 
                f"</head><body><h1>{name}</h1><table><thead><tr><th>Day</th><th>Exercise</th><th>Pattern</th><th>Sets</th><th>Reps</th><th>Rest(s)</th><th>Notes</th></tr></thead><tbody>{''.join(rows)}</tbody></table></body></html>"
            )
            resp = Response(html)
            resp["Content-Type"] = "text/html; charset=utf-8"
            return resp

        # CSV default
        buf = StringIO()
        w = _csv.writer(buf)
        w.writerow(["Day", "Exercise", "Movement Pattern", "Sets", "Reps", "Rest (s)", "Notes", "Equipment"])
        for day, it in entries:
            w.writerow([
                day,
                it.get("name") or it.get("exercise") or "Exercise",
                it.get("movement_pattern") or "",
                it.get("sets") or "",
                it.get("reps") or "",
                it.get("rest_s") or it.get("rest") or "",
                it.get("notes") or "",
                it.get("equipment") or "",
            ])
        resp = Response(buf.getvalue())
        resp["Content-Type"] = "text/csv; charset=utf-8"
        resp["Content-Disposition"] = f"attachment; filename={name}.csv"
        return resp

    @action(detail=True, methods=["post"], url_path=r"blocks/(?P<block_id>[^/.]+)/next")
    def block_next(self, request, pk=None, block_id=None):
        client = get_object_or_404(Client, pk=pk)
        block = get_object_or_404(ClientBlock, pk=block_id, client=client)
        name = (request.data or {}).get("name") or f"Next of {block.name or block.id}"
        data = block.block
        def bump(x):
            try:
                return max(2, min(6, int(x) + 1))
            except Exception:
                return x
        # Shallow copy and bump first 2 items per day
        new_block = {}
        if isinstance(data, dict):
            for day, arr in data.items():
                if isinstance(arr, list):
                    bumped = []
                    cnt = 0
                    for it in arr:
                        it2 = dict(it)
                        if cnt < 2 and isinstance(it2.get("sets"), (int, float)):
                            it2["sets"] = bump(it2.get("sets"))
                            cnt += 1
                        bumped.append(it2)
                    new_block[day] = bumped
        elif isinstance(data, list):
            new_block = []
            for arr in data:
                if isinstance(arr, list):
                    bumped = []
                    cnt = 0
                    for it in arr:
                        it2 = dict(it)
                        if cnt < 2 and isinstance(it2.get("sets"), (int, float)):
                            it2["sets"] = bump(it2.get("sets"))
                            cnt += 1
                        bumped.append(it2)
                    new_block.append(bumped)
        cb = ClientBlock.objects.create(client=client, name=name, block=new_block)
        return Response(ClientBlockSerializer(cb).data, status=status.HTTP_201_CREATED)
