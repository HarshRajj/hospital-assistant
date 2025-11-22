import VoiceAssistant from "./components/VoiceAssistant";
import ChatAssistant from "./components/ChatAssistant";

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50/50 selection:bg-blue-100 selection:text-blue-900">
      {/* Header */}
      <header className="sticky top-0 z-50 glass border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white text-2xl shadow-lg shadow-blue-600/20">
                🏥
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 tracking-tight">Arogya Med-City</h1>
                <p className="text-xs text-gray-500 font-medium tracking-wide uppercase">Premium Healthcare</p>
              </div>
            </div>
            <div className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-600">
              <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-red-50 text-red-600 border border-red-100">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
                </span>
                Emergency: 911
              </div>
              <div className="flex items-center gap-2 text-green-600">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                24/7 Available
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-20">
        {/* Hero Section */}
        <section className="text-center space-y-6 relative">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-blue-100/50 rounded-full blur-3xl -z-10"></div>
          <h2 className="text-5xl md:text-6xl font-bold text-gray-900 tracking-tight">
            Your Health, <span className="text-gradient">Our Priority</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Experience world-class healthcare with our state-of-the-art facilities.
            Connect with our AI assistants for instant support.
          </p>
        </section>

        {/* AI Assistants Grid */}
        <section className="grid lg:grid-cols-2 gap-8 items-start">
          <div className="space-y-4">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl">🎤</span>
              <h3 className="text-xl font-bold text-gray-900">Voice Assistant</h3>
            </div>
            <VoiceAssistant />
          </div>
          <div className="space-y-4">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl">💬</span>
              <h3 className="text-xl font-bold text-gray-900">Chat Support</h3>
            </div>
            <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-100 overflow-hidden">
              <ChatAssistant />
            </div>
          </div>
        </section>

        {/* Departments Grid */}
        <section>
          <div className="flex items-center justify-between mb-10">
            <div>
              <h3 className="text-3xl font-bold text-gray-900">Specialized Departments</h3>
              <p className="text-gray-500 mt-2">Comprehensive care across all specialties</p>
            </div>
            <button className="hidden md:block text-blue-600 font-medium hover:text-blue-700">
              View All Departments →
            </button>
          </div>

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
        <section className="grid md:grid-cols-3 gap-6">
          <InfoCard
            icon="🕒"
            title="Visiting Hours"
            info={["General Ward: 4 PM - 7 PM", "ICU: 11 AM - 12 PM, 5 PM - 6 PM"]}
          />
          <InfoCard
            icon="🍽️"
            title="Cafeteria"
            info={["Breakfast: 6:30 AM - 9:30 AM", "Lunch: 12:00 PM - 3:00 PM", "Dinner: 6:00 PM - 9:00 PM"]}
          />
          <InfoCard
            icon="🏥"
            title="Facilities"
            info={["Free Parking Available", "24/7 Emergency Services", "Ambulance Services"]}
          />
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-100 py-12 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div className="col-span-2">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white text-lg">
                  🏥
                </div>
                <span className="text-xl font-bold text-gray-900">Arogya Med-City</span>
              </div>
              <p className="text-gray-500 max-w-xs">
                Leading the way in medical excellence with cutting-edge technology and compassionate care.
              </p>
            </div>
            <div>
              <h4 className="font-bold text-gray-900 mb-4">Quick Links</h4>
              <ul className="space-y-2 text-gray-500 text-sm">
                <li><a href="#" className="hover:text-blue-600">About Us</a></li>
                <li><a href="#" className="hover:text-blue-600">Doctors</a></li>
                <li><a href="#" className="hover:text-blue-600">Appointments</a></li>
                <li><a href="#" className="hover:text-blue-600">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-gray-900 mb-4">Contact</h4>
              <ul className="space-y-2 text-gray-500 text-sm">
                <li>123 Health Avenue</li>
                <li>Medical District, City</li>
                <li>+1 (555) 123-4567</li>
                <li>info@arogyamed.com</li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-gray-100 text-center text-gray-400 text-sm">
            <p>© 2025 Arogya Med-City Hospital. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

function DepartmentCard({ icon, title, description, floor }: { icon: string; title: string; description: string; floor: string }) {
  return (
    <div className="group bg-white rounded-2xl p-6 border border-gray-100 card-hover cursor-pointer">
      <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-2xl mb-4 group-hover:bg-blue-600 group-hover:text-white transition-colors">
        {icon}
      </div>
      <h4 className="text-xl font-bold text-gray-900 mb-2">{title}</h4>
      <p className="text-gray-500 text-sm mb-4 leading-relaxed">{description}</p>
      <div className="flex items-center gap-2 text-xs font-medium text-blue-600 bg-blue-50 w-fit px-3 py-1.5 rounded-full">
        <span>📍</span>
        {floor}
      </div>
    </div>
  );
}

function InfoCard({ icon, title, info }: { icon: string; title: string; info: string[] }) {
  return (
    <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-gray-50 rounded-full flex items-center justify-center text-xl">
          {icon}
        </div>
        <h4 className="text-lg font-bold text-gray-900">{title}</h4>
      </div>
      <ul className="space-y-3">
        {info.map((item, index) => (
          <li key={index} className="text-gray-600 text-sm flex items-center gap-3">
            <span className="w-1.5 h-1.5 bg-blue-400 rounded-full"></span>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
