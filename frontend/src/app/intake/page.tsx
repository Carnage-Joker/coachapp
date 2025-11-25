'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function IntakePage() {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    age_group: '25-34',
    primary_location: 'Home',
    space_available: 'Medium',
    impact_tolerance: 'Moderate',
    session_length_min: 45,
    days_per_week: 3,
    goals: [] as string[],
    knee_issue: false,
    shoulder_issue: false,
    back_issue: false,
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000'
      const token = localStorage.getItem('access_token')
      
      if (!token) {
        setError('Please login first')
        setLoading(false)
        return
      }

      const response = await fetch(`${apiBase}/api/clients/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to create client')
      }

      setSuccess(true)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleGoalToggle = (goal: string) => {
    setFormData(prev => ({
      ...prev,
      goals: prev.goals.includes(goal)
        ? prev.goals.filter(g => g !== goal)
        : [...prev.goals, goal]
    }))
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full text-center">
          <div className="text-6xl mb-4">✅</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Client Created Successfully!</h2>
          <p className="text-gray-600 mb-6">Your client profile has been created and a personalized workout plan is ready.</p>
          <Link href="/dashboard" className="bg-brand-600 text-white px-6 py-3 rounded-lg inline-block hover:bg-brand-700 transition">
            Go to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-brand-100">
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="text-2xl font-bold text-brand-600">Dig Deep Fitness</Link>
            <Link href="/dashboard" className="text-gray-700 hover:text-brand-600">Dashboard</Link>
          </div>
        </div>
      </nav>

      <div className="max-w-3xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Client Intake Form</h1>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-lg p-8 space-y-6">
          {/* Personal Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">First Name</label>
              <input
                type="text"
                required
                value={formData.first_name}
                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
              <input
                type="text"
                required
                value={formData.last_name}
                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Age Group</label>
            <select
              value={formData.age_group}
              onChange={(e) => setFormData({ ...formData, age_group: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
            >
              <option>Under 18</option>
              <option>18-24</option>
              <option>25-34</option>
              <option>35-44</option>
              <option>45-54</option>
              <option>55-64</option>
              <option>65+</option>
            </select>
          </div>

          {/* Training Details */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Training Details</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Primary Location</label>
                <select
                  value={formData.primary_location}
                  onChange={(e) => setFormData({ ...formData, primary_location: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                >
                  <option>Home</option>
                  <option>Gym</option>
                  <option>Outdoor</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Space Available</label>
                <select
                  value={formData.space_available}
                  onChange={(e) => setFormData({ ...formData, space_available: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                >
                  <option>Small</option>
                  <option>Medium</option>
                  <option>Large</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Days per Week</label>
                <input
                  type="number"
                  min="1"
                  max="7"
                  value={formData.days_per_week}
                  onChange={(e) => setFormData({ ...formData, days_per_week: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Session Length (minutes)</label>
                <input
                  type="number"
                  min="15"
                  max="120"
                  step="15"
                  value={formData.session_length_min}
                  onChange={(e) => setFormData({ ...formData, session_length_min: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Impact Tolerance</label>
              <select
                value={formData.impact_tolerance}
                onChange={(e) => setFormData({ ...formData, impact_tolerance: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              >
                <option>Low</option>
                <option>Moderate</option>
                <option>High</option>
              </select>
            </div>
          </div>

          {/* Goals */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Training Goals</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {['Fat Loss', 'Strength', 'Hypertrophy', 'Conditioning', 'Mobility', 'Power', 'Rehab'].map(goal => (
                <button
                  key={goal}
                  type="button"
                  onClick={() => handleGoalToggle(goal)}
                  className={`px-4 py-2 rounded-lg border-2 transition ${
                    formData.goals.includes(goal)
                      ? 'bg-brand-600 text-white border-brand-600'
                      : 'bg-white text-gray-700 border-gray-300 hover:border-brand-400'
                  }`}
                >
                  {goal}
                </button>
              ))}
            </div>
          </div>

          {/* Injuries */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Injury History</h3>
            <div className="space-y-3">
              {[
                { key: 'knee_issue', label: 'Knee Issues' },
                { key: 'shoulder_issue', label: 'Shoulder Issues' },
                { key: 'back_issue', label: 'Back Issues' },
              ].map(({ key, label }) => (
                <label key={key} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData[key as keyof typeof formData] as boolean}
                    onChange={(e) => setFormData({ ...formData, [key]: e.target.checked })}
                    className="w-5 h-5 text-brand-600 border-gray-300 rounded focus:ring-brand-500"
                  />
                  <span className="ml-3 text-gray-700">{label}</span>
                </label>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-brand-600 text-white py-3 rounded-lg font-medium hover:bg-brand-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating Client...' : 'Create Client & Generate Plan'}
          </button>
        </form>
      </div>
    </div>
  )
}
