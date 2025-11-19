import VoiceAssistant from "./components/VoiceAssistant";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="text-4xl">🏥</div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Arogya Med-City Hospital</h1>
                <p className="text-sm text-gray-600">Your Health, Our Priority</p>
              </div>
            </div>
            <div className="hidden md:flex items-center gap-6 text-sm text-gray-700">
              <div className="flex items-center gap-2">
                <span className="text-xl">📞</span>
                <span>Emergency: 911</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xl">⏰</span>
                <span>24/7 Available</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <section className="mb-12 text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Welcome to Arogya Med-City Hospital
          </h2>
          <p className="text-xl text-gray-700 max-w-3xl mx-auto">
            Experience world-class healthcare with our state-of-the-art facilities and expert medical professionals. 
            Try our AI Voice Assistant for instant information!
          </p>
        </section>

        {/* Voice Assistant Section */}
        <section className="mb-16">
          <VoiceAssistant />
        </section>

        {/* Departments Grid */}
        <section className="mb-16">
          <h3 className="text-3xl font-bold text-gray-900 mb-8 text-center">Our Departments</h3>
          <div className="grid md:grid-cols-3 gap-6">
            <DepartmentCard 
              icon="❤️"
              title="Cardiology"
              description="Expert heart care with advanced diagnostics and treatment"
              floor="2nd Floor, East Wing"
            />
            <DepartmentCard 
              icon="👶"
              title="Pediatrics"
              description="Specialized care for infants, children, and adolescents"
              floor="3rd Floor, West Wing"
            />
            <DepartmentCard 
              icon="🦴"
              title="Orthopedics"
              description="Comprehensive bone and joint treatment services"
              floor="1st Floor, North Wing"
            />
            <DepartmentCard 
              icon="🧠"
              title="Neurology"
              description="Advanced neurological care and treatment"
              floor="4th Floor, East Wing"
            />
            <DepartmentCard 
              icon="🔬"
              title="Oncology"
              description="State-of-the-art cancer diagnosis and treatment"
              floor="5th Floor, South Wing"
            />
            <DepartmentCard 
              icon="👁️"
              title="Ophthalmology"
              description="Complete eye care and vision correction services"
              floor="2nd Floor, West Wing"
            />
          </div>
        </section>

        {/* Quick Info */}
        <section className="grid md:grid-cols-3 gap-6 mb-16">
          <InfoCard
            icon="🕒"
            title="Visiting Hours"
            info={["General Ward: 4 PM - 7 PM", "ICU: 11 AM - 12 PM, 5 PM - 6 PM"]}
          />
          <InfoCard
            icon="🍽️"
            title="Cafeteria Hours"
            info={["Breakfast: 6:30 AM - 9:30 AM", "Lunch: 12:00 PM - 3:00 PM", "Dinner: 6:00 PM - 9:00 PM"]}
          />
          <InfoCard
            icon="🚗"
            title="Facilities"
            info={["Free Parking Available", "24/7 Emergency Services", "Ambulance Services"]}
          />
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400">© 2025 Arogya Med-City Hospital. All rights reserved.</p>
          <p className="text-gray-500 text-sm mt-2">Powered by AI Voice Assistant Technology</p>
        </div>
      </footer>
    </div>
  );
}

function DepartmentCard({ icon, title, description, floor }: { icon: string; title: string; description: string; floor: string }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="text-4xl mb-3">{icon}</div>
      <h4 className="text-xl font-bold text-gray-900 mb-2">{title}</h4>
      <p className="text-gray-600 text-sm mb-3">{description}</p>
      <p className="text-blue-600 text-sm font-medium">📍 {floor}</p>
    </div>
  );
}

function InfoCard({ icon, title, info }: { icon: string; title: string; info: string[] }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="text-3xl mb-3">{icon}</div>
      <h4 className="text-lg font-bold text-gray-900 mb-3">{title}</h4>
      <ul className="space-y-1">
        {info.map((item, index) => (
          <li key={index} className="text-gray-600 text-sm">{item}</li>
        ))}
      </ul>
    </div>
  );
}
