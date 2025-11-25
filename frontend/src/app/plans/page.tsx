'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

interface Exercise {
  name: string
  movement_pattern?: string
  equipment?: string
  sets: number
  reps: number | string
  rest_s: number
  notes?: string
}

interface WorkoutPlan {
  client: string
  plan: {
    [day: string]: Exercise[]
  }
}

interface Client {
  id: string
  first_name: string
  last_name: string
  preferred_name: string
}

export default function PlansPage() {
  const router = useRouter()
  const [clients, setClients] = useState<Client[]>([])
  const [selectedClientId, setSelectedClientId] = useState<string>('')
  const [plan, setPlan] = useState<WorkoutPlan | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/login')
      return
    }
    fetchClients()
  }, [])

  const fetchClients = async () => {
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000'
      const token = localStorage.getItem('access_token')
      
      const response = await fetch(`${apiBase}/api/clients/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) throw new Error('Failed to fetch clients')

      const data = await response.json()
      setClients(data.results || data)
    } catch (err: any) {
      setError(err.message)
    }
  }

  const generatePlan = async () => {
    if (!selectedClientId) {
      setError('Please select a client')
      return
    }

    setLoading(true)
    setError('')
    setPlan(null)

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000'
      const token = localStorage.getItem('access_token')
      
      const response = await fetch(`${apiBase}/api/clients/${selectedClientId}/plan/?save=false`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) throw new Error('Failed to generate plan')

      const data = await response.json()
      setPlan(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const savePlan = async () => {
    if (!selectedClientId) return

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000'
      const token = localStorage.getItem('access_token')
      
      const response = await fetch(`${apiBase}/api/clients/${selectedClientId}/plan/?save=true`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) throw new Error('Failed to save plan')

      alert('Plan saved successfully!')
    } catch (err: any) {
      alert('Error: ' + err.message)
    }
  }

  const formatReps = (reps: number | string): string => {
    if (typeof reps === 'string') return reps
    return reps.toString()
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-brand-100">
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-8">
              <Link href="/" className="text-2xl font-bold text-brand-600">Dig Deep Fitness</Link>
              <Link href="/dashboard" className="text-gray-700 hover:text-brand-600 font-medium">
                Dashboard
              </Link>
              <Link href="/plans" className="text-brand-600 font-medium border-b-2 border-brand-600">
                Generate Plans
              </Link>
              <Link href="/exercises" className="text-gray-700 hover:text-brand-600 font-medium">
                Exercises
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Workout Plan Generator</h1>
          <p className="text-gray-600">Create personalized training programs for your clients</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex items-end gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">Select Client</label>
              <select
                value={selectedClientId}
                onChange={(e) => setSelectedClientId(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              >
                <option value="">Choose a client...</option>
                {clients.map((client) => (
                  <option key={client.id} value={client.id}>
                    {client.preferred_name || `${client.first_name} ${client.last_name}`}
                  </option>
                ))}
              </select>
            </div>
            <button
              onClick={generatePlan}
              disabled={loading || !selectedClientId}
              className="bg-brand-600 text-white px-6 py-2 rounded-lg hover:bg-brand-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Generating...' : 'Generate Plan'}
            </button>
          </div>
        </div>

        {plan && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  Training Plan for {plan.client}
                </h2>
                <button
                  onClick={savePlan}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
                >
                  Save Plan
                </button>
              </div>

              {Object.entries(plan.plan).map(([day, exercises]) => (
                <div key={day} className="mb-8 last:mb-0">
                  <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                    <span className="bg-brand-600 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3">
                      {day.split(' ')[1]}
                    </span>
                    {day}
                  </h3>
                  
                  <div className="space-y-3">
                    {exercises.map((exercise, idx) => (
                      <div
                        key={idx}
                        className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition"
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h4 className="font-semibold text-gray-900 mb-1">
                              {idx + 1}. {exercise.name}
                            </h4>
                            <div className="flex flex-wrap gap-2 text-sm text-gray-600">
                              {exercise.movement_pattern && (
                                <span className="inline-flex items-center px-2 py-1 rounded bg-blue-100 text-blue-800">
                                  {exercise.movement_pattern}
                                </span>
                              )}
                              {exercise.equipment && (
                                <span className="inline-flex items-center px-2 py-1 rounded bg-purple-100 text-purple-800">
                                  {exercise.equipment}
                                </span>
                              )}
                            </div>
                            {exercise.notes && (
                              <p className="text-sm text-gray-600 mt-2 italic">{exercise.notes}</p>
                            )}
                          </div>
                          <div className="ml-4 text-right">
                            <div className="font-semibold text-brand-600">
                              {exercise.sets} × {formatReps(exercise.reps)}
                            </div>
                            <div className="text-sm text-gray-600">
                              {exercise.rest_s}s rest
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {exercises.length === 0 && (
                    <p className="text-gray-500 italic">No exercises for this day</p>
                  )}
                </div>
              ))}
            </div>

            <div className="bg-brand-50 rounded-lg p-6 border border-brand-200">
              <h3 className="font-semibold text-brand-900 mb-2">💡 Training Tips</h3>
              <ul className="space-y-1 text-sm text-brand-800">
                <li>• Ensure proper warm-up before starting each session</li>
                <li>• Focus on movement quality over speed</li>
                <li>• Adjust weights/resistance based on target RPE</li>
                <li>• Track progress weekly and adjust as needed</li>
                <li>• Stay hydrated and maintain proper nutrition</li>
              </ul>
            </div>
          </div>
        )}

        {!plan && !loading && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-6xl mb-4">🏋️</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Plan Generated Yet</h3>
            <p className="text-gray-600">Select a client and click "Generate Plan" to create a personalized workout program</p>
          </div>
        )}
      </div>
    </div>
  )
}
