'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

interface Client {
  id: string
  first_name: string
  last_name: string
  preferred_name: string
  email: string
  age_group: string
  primary_location: string
  days_per_week: number
  goals: string[]
  created_at: string
}

export default function DashboardPage() {
  const router = useRouter()
  const [clients, setClients] = useState<Client[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/login')
      return
    }

    fetchUser()
    fetchClients()
  }, [])

  const fetchUser = async () => {
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000'
      const token = localStorage.getItem('access_token')
      
      const response = await fetch(`${apiBase}/api/auth/me/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setUser(data)
      }
    } catch (err) {
      console.error('Failed to fetch user:', err)
    }
  }

  const fetchClients = async () => {
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000'
      const token = localStorage.getItem('access_token')
      
      const response = await fetch(`${apiBase}/api/clients/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to fetch clients')
      }

      const data = await response.json()
      setClients(data.results || data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    router.push('/')
  }

  const generatePlan = async (clientId: string) => {
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000'
      const token = localStorage.getItem('access_token')
      
      const response = await fetch(`${apiBase}/api/clients/${clientId}/plan/?save=true`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to generate plan')
      }

      const plan = await response.json()
      alert('Workout plan generated successfully!')
      console.log('Plan:', plan)
    } catch (err: any) {
      alert('Error: ' + err.message)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-brand-100">
      {/* Navigation */}
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-8">
              <Link href="/" className="text-2xl font-bold text-brand-600">Dig Deep Fitness</Link>
              <Link href="/dashboard" className="text-gray-700 hover:text-brand-600 font-medium">
                Dashboard
              </Link>
              <Link href="/intake" className="text-gray-700 hover:text-brand-600 font-medium">
                New Client
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              {user && (
                <span className="text-gray-700">Welcome, {user.username}!</span>
              )}
              <button
                onClick={handleLogout}
                className="text-gray-700 hover:text-brand-600 font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Dashboard Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Coach Dashboard</h1>
          <p className="text-gray-600">Manage your clients and their training programs</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl font-bold text-brand-600 mb-2">{clients.length}</div>
            <div className="text-gray-600">Total Clients</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl font-bold text-green-600 mb-2">
              {clients.filter(c => c.days_per_week >= 3).length}
            </div>
            <div className="text-gray-600">Active Training</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl font-bold text-purple-600 mb-2">
              {clients.reduce((sum, c) => sum + c.days_per_week, 0)}
            </div>
            <div className="text-gray-600">Weekly Sessions</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl font-bold text-orange-600 mb-2">60+</div>
            <div className="text-gray-600">Exercises Available</div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              href="/intake"
              className="flex items-center justify-center bg-brand-600 text-white px-6 py-4 rounded-lg hover:bg-brand-700 transition"
            >
              <span className="text-2xl mr-3">➕</span>
              <span className="font-medium">Add New Client</span>
            </Link>
            <button className="flex items-center justify-center bg-purple-600 text-white px-6 py-4 rounded-lg hover:bg-purple-700 transition">
              <span className="text-2xl mr-3">📊</span>
              <span className="font-medium">View Analytics</span>
            </button>
            <button className="flex items-center justify-center bg-green-600 text-white px-6 py-4 rounded-lg hover:bg-green-700 transition">
              <span className="text-2xl mr-3">📅</span>
              <span className="font-medium">Schedule Session</span>
            </button>
          </div>
        </div>

        {/* Clients List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Your Clients</h2>
          
          {loading && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading clients...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {!loading && !error && clients.length === 0 && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">👥</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No clients yet</h3>
              <p className="text-gray-600 mb-6">Start by adding your first client</p>
              <Link
                href="/intake"
                className="bg-brand-600 text-white px-6 py-3 rounded-lg inline-block hover:bg-brand-700 transition"
              >
                Add Client
              </Link>
            </div>
          )}

          {!loading && !error && clients.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Name</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Email</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Location</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Days/Week</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Goals</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {clients.map((client) => (
                    <tr key={client.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-4 px-4">
                        <div className="font-medium text-gray-900">
                          {client.preferred_name || `${client.first_name} ${client.last_name}`}
                        </div>
                        <div className="text-sm text-gray-500">{client.age_group}</div>
                      </td>
                      <td className="py-4 px-4 text-gray-600">{client.email || '-'}</td>
                      <td className="py-4 px-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {client.primary_location}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-gray-600">{client.days_per_week}</td>
                      <td className="py-4 px-4">
                        <div className="flex flex-wrap gap-1">
                          {client.goals.slice(0, 2).map((goal, i) => (
                            <span
                              key={i}
                              className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800"
                            >
                              {goal}
                            </span>
                          ))}
                          {client.goals.length > 2 && (
                            <span className="text-xs text-gray-500">+{client.goals.length - 2}</span>
                          )}
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <button
                          onClick={() => generatePlan(client.id)}
                          className="text-brand-600 hover:text-brand-700 font-medium text-sm"
                        >
                          Generate Plan
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
