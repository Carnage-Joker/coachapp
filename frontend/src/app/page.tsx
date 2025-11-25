import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-brand-50 to-brand-100">
      {/* Navigation */}
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-brand-600">Dig Deep Fitness</h1>
            </div>
            <div className="flex space-x-4">
              <Link href="/login" className="text-gray-700 hover:text-brand-600 px-3 py-2 rounded-md text-sm font-medium">
                Login
              </Link>
              <Link href="/register" className="bg-brand-600 text-white hover:bg-brand-700 px-4 py-2 rounded-md text-sm font-medium">
                Sign Up
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h2 className="text-5xl font-extrabold text-gray-900 mb-6">
            Transform Your Training Journey
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Premium fitness platform designed for personal trainers and clients to maximize progress 
            and develop a healthier, stronger you. AI-powered workout generation, progress tracking, 
            and personalized training programs.
          </p>
          <div className="flex justify-center space-x-4">
            <Link href="/register" className="bg-brand-600 text-white hover:bg-brand-700 px-8 py-4 rounded-lg text-lg font-medium shadow-lg transition">
              Get Started Free
            </Link>
            <Link href="/demo" className="bg-white text-brand-600 hover:bg-gray-50 px-8 py-4 rounded-lg text-lg font-medium shadow-lg border-2 border-brand-600 transition">
              View Demo
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-4xl mb-4">🎯</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Smart Workout Generation</h3>
            <p className="text-gray-600">
              AI-powered algorithms create personalized workouts based on your goals, equipment, 
              and fitness level.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Progress Tracking</h3>
            <p className="text-gray-600">
              Track your gains with detailed analytics, charts, and progress photos. 
              See your transformation over time.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-4xl mb-4">👥</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Client Management</h3>
            <p className="text-gray-600">
              Coaches can manage multiple clients, create custom programs, and monitor 
              progress in real-time.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-4xl mb-4">💪</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Exercise Library</h3>
            <p className="text-gray-600">
              Access 60+ exercises with detailed instructions, video demonstrations, 
              and coaching cues.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-4xl mb-4">📅</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Session Booking</h3>
            <p className="text-gray-600">
              Easy scheduling system for training sessions, consultations, and check-ins 
              with automatic reminders.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-4xl mb-4">🏆</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Gamification</h3>
            <p className="text-gray-600">
              Earn achievements, track streaks, and compete with yourself. 
              Stay motivated with rewards.
            </p>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-20 bg-brand-600 rounded-2xl p-12 text-center text-white">
          <h3 className="text-3xl font-bold mb-4">Ready to Transform Your Training?</h3>
          <p className="text-xl mb-8">Join thousands of coaches and clients achieving their fitness goals</p>
          <Link href="/register" className="bg-white text-brand-600 hover:bg-gray-100 px-8 py-4 rounded-lg text-lg font-medium inline-block transition">
            Start Your Journey Today
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p>&copy; 2024 Dig Deep Fitness Platform. All rights reserved.</p>
          <p className="mt-2 text-gray-400">Building healthier humans, one workout at a time.</p>
        </div>
      </footer>
    </main>
  )
}
