'use client'

import { useState } from 'react'
import Link from 'next/link'

interface DemoExercise {
  name: string
  pattern: string
  equipment: string
  level: string
  muscle: string
  sets: string
  reps: string
  rest: string
  cues: string
  homeFriendly?: boolean
  kneeFriendly?: boolean
  shoulderFriendly?: boolean
  backFriendly?: boolean
}

// Demo exercises data
const demoExercisesData: DemoExercise[] = [
  {
    name: 'Goblet Squat',
    pattern: 'Squat',
    equipment: 'Dumbbells',
    level: 'Beginner',
    muscle: 'Quadriceps',
    sets: '3',
    reps: '10',
    rest: '60s',
    cues: 'Keep chest up, elbows inside knees, weight on heels',
    homeFriendly: true,
    kneeFriendly: true,
  },
  {
    name: 'Romanian Deadlift',
    pattern: 'Hinge',
    equipment: 'Dumbbells',
    level: 'Beginner',
    muscle: 'Hamstrings',
    sets: '3',
    reps: '8',
    rest: '90s',
    cues: 'Soft knees, hinge at hips, neutral spine, shoulders back',
    homeFriendly: true,
    backFriendly: false,
  },
  {
    name: 'Push-Up',
    pattern: 'Horizontal Push',
    equipment: 'Bodyweight',
    level: 'Beginner',
    muscle: 'Chest',
    sets: '3',
    reps: '12',
    rest: '60s',
    cues: 'Hands under shoulders, tight core, full range, elbows 45°',
    homeFriendly: true,
    shoulderFriendly: false,
  },
  {
    name: 'Inverted Row',
    pattern: 'Horizontal Pull',
    equipment: 'Rings',
    level: 'Intermediate',
    muscle: 'Back',
    sets: '3',
    reps: '10',
    rest: '60s',
    cues: 'Pull chest to bar, squeeze shoulder blades, control descent',
    homeFriendly: true,
    shoulderFriendly: true,
  },
  {
    name: 'Plank',
    pattern: 'Core – Brace/Anti-Extension',
    equipment: 'Bodyweight',
    level: 'Beginner',
    muscle: 'Abs',
    sets: '3',
    reps: '30s hold',
    rest: '45s',
    cues: 'Straight line, tight core, squeeze glutes, neutral neck',
    homeFriendly: true,
    backFriendly: false,
  },
]

export default function ExercisesPage() {
  const [filteredExercises, setFilteredExercises] = useState<DemoExercise[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedEquipment, setSelectedEquipment] = useState<string>('all')
  const [selectedMovement, setSelectedMovement] = useState<string>('all')
  const [selectedLevel, setSelectedLevel] = useState<string>('all')

  useEffect(() => {
    let filtered = demoExercisesData

    if (searchTerm) {
      filtered = filtered.filter(ex =>
        ex.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ex.pattern.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ex.muscle.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    if (selectedEquipment !== 'all') {
      filtered = filtered.filter(ex => ex.equipment === selectedEquipment)
    }

    if (selectedMovement !== 'all') {
      filtered = filtered.filter(ex => ex.pattern === selectedMovement)
    }

    if (selectedLevel !== 'all') {
      filtered = filtered.filter(ex => ex.level === selectedLevel)
    }

    setFilteredExercises(filtered)
  }, [searchTerm, selectedEquipment, selectedMovement, selectedLevel])

  const equipmentOptions = ['Bodyweight', 'Dumbbells', 'Kettlebell', 'Barbell', 'Rings', 'Gym Equipment', 'Cable/Machine', 'Bands/Chains', 'Strongman', 'Med Ball', 'Cardio Machine']
  const movementOptions = ['Squat', 'Hinge', 'Horizontal Push', 'Horizontal Pull', 'Vertical Push', 'Vertical Pull', 'Lunge', 'Core – Brace/Anti-Extension', 'Carry/Gait', 'Jump/Power', 'Conditioning']
  const levelOptions = ['Beginner', 'Intermediate', 'Advanced']

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
              <Link href="/plans" className="text-gray-700 hover:text-brand-600 font-medium">
                Generate Plans
              </Link>
              <Link href="/exercises" className="text-brand-600 font-medium border-b-2 border-brand-600">
                Exercises
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Exercise Library</h1>
          <p className="text-gray-600">Browse 60+ exercises with detailed instructions and coaching cues</p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
              <input
                type="text"
                placeholder="Search exercises..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Equipment</label>
              <select
                value={selectedEquipment}
                onChange={(e) => setSelectedEquipment(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              >
                <option value="all">All Equipment</option>
                {equipmentOptions.map(eq => (
                  <option key={eq} value={eq}>{eq}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Movement Pattern</label>
              <select
                value={selectedMovement}
                onChange={(e) => setSelectedMovement(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              >
                <option value="all">All Patterns</option>
                {movementOptions.map(mv => (
                  <option key={mv} value={mv}>{mv}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Skill Level</label>
              <select
                value={selectedLevel}
                onChange={(e) => setSelectedLevel(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              >
                <option value="all">All Levels</option>
                {levelOptions.map(lv => (
                  <option key={lv} value={lv}>{lv}</option>
                ))}
              </select>
            </div>
          </div>

          {!isLoading && (
          <div className="text-sm text-gray-600">
            Showing {exercises.length > 0 ? filteredExercises.length : demoExercises.length} exercises
          </div>
          )}
        </div>

        {/* Exercise Cards */}
        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-600"></div>
          </div>
        ) : exercises.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredExercises.map((exercise, idx) => (
            <div key={idx} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-1">{exercise.Exercise}</h3>
                  <p className="text-sm text-gray-600">{exercise['Primary Muscle Group']}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  exercise['Skill Level'] === 'Beginner' ? 'bg-green-100 text-green-800' :
                  exercise['Skill Level'] === 'Intermediate' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {exercise['Skill Level']}
                </span>
              </div>

              <div className="flex flex-wrap gap-2 mb-4">
                <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                  {exercise['Movement Pattern']}
                </span>
                <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800">
                  {exercise.Equipment}
                </span>
                {exercise['Home-Friendly'] === 'Yes' && (
                  <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-emerald-100 text-emerald-800">
                    🏠 Home
                  </span>
                )}
              </div>

              <div className="bg-gray-50 rounded-lg p-3 mb-4">
                <div className="flex justify-between text-sm">
                  <div>
                    <span className="text-gray-600">Sets:</span>
                    <span className="font-medium text-gray-900 ml-1">{exercise['Default Sets']}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Reps:</span>
                    <span className="font-medium text-gray-900 ml-1">{exercise['Default Reps']}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Rest:</span>
                    <span className="font-medium text-gray-900 ml-1">{exercise['Default Rest (s)']}s</span>
                  </div>
                </div>
              </div>

              <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-1">Coaching Cues:</h4>
                <p className="text-sm text-gray-600 italic">{exercise['Coaching Cues']}</p>
              </div>

              <div className="flex flex-wrap gap-2">
                {exercise['Knee-Friendly'] === 'Yes' && (
                  <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-green-50 text-green-700">
                    ✓ Knee Friendly
                  </span>
                )}
                {exercise['Shoulder-Friendly'] === 'Yes' && (
                  <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-green-50 text-green-700">
                    ✓ Shoulder Friendly
                  </span>
                )}
                {exercise['Shoulder-Friendly'] === 'No' && (
                  <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-orange-50 text-orange-700">
                    ⚠ Shoulder Caution
                  </span>
                )}
                {exercise['Back-Friendly'] === 'No' && (
                  <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-orange-50 text-orange-700">
                    ⚠ Back Caution
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
        ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredExercises.map((exercise, idx) => (
            <div key={idx} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-1">{exercise.name}</h3>
                  <p className="text-sm text-gray-600">{exercise.muscle}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  exercise.level === 'Beginner' ? 'bg-green-100 text-green-800' :
                  exercise.level === 'Intermediate' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {exercise.level}
                </span>
              </div>

              <div className="flex flex-wrap gap-2 mb-4">
                <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                  {exercise.pattern}
                </span>
                <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800">
                  {exercise.equipment}
                </span>
                {exercise.homeFriendly && (
                  <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-emerald-100 text-emerald-800">
                    🏠 Home
                  </span>
                )}
              </div>

              <div className="bg-gray-50 rounded-lg p-3 mb-4">
                <div className="flex justify-between text-sm">
                  <div>
                    <span className="text-gray-600">Sets:</span>
                    <span className="font-medium text-gray-900 ml-1">{exercise.sets}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Reps:</span>
                    <span className="font-medium text-gray-900 ml-1">{exercise.reps}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Rest:</span>
                    <span className="font-medium text-gray-900 ml-1">{exercise.rest}</span>
                  </div>
                </div>
              </div>

              <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-1">Coaching Cues:</h4>
                <p className="text-sm text-gray-600 italic">{exercise.cues}</p>
              </div>

              <div className="flex flex-wrap gap-2">
                {exercise.kneeFriendly && (
                  <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-green-50 text-green-700">
                    ✓ Knee Friendly
                  </span>
                )}
                {exercise.shoulderFriendly === true && (
                  <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-green-50 text-green-700">
                    ✓ Shoulder Friendly
                  </span>
                )}
                {exercise.shoulderFriendly === false && (
                  <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-orange-50 text-orange-700">
                    ⚠ Shoulder Caution
                  </span>
                )}
                {exercise.backFriendly === false && (
                  <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-orange-50 text-orange-700">
                    ⚠ Back Caution
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
        )}

        <div className="mt-8 text-center">
          <p className="text-gray-600">
            Want to see the full exercise library? Connect to the API to access all 60+ exercises with video demonstrations.
          </p>
        </div>
      </div>
    </div>
  )
}
