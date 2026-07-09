import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

export const GaragePage = () => {
  const vehicles = [
    { id: 'bmw-m3', name: 'BMW M3', year: '2024', hp: 503, img: 'BMW M3' },
    { id: 'mustang-gt', name: 'Mustang GT', year: '2024', hp: 480, img: 'Mustang GT' },
    { id: 'audi-rs6', name: 'Audi RS6', year: '2024', hp: 591, img: 'RS6' },
    { id: 'amg-gt', name: 'AMG GT', year: '2024', hp: 577, img: 'AMG GT' },
    { id: 'supra', name: 'GR Supra', year: '2024', hp: 382, img: 'Supra' },
    { id: 'gtr', name: 'GT-R', year: '2024', hp: 565, img: 'GT-R' },
  ]

  const partsCategories = [
    'Turbochargers', 'Intercoolers', 'Exhaust Systems', 'Air Intake Systems',
    'Suspension', 'Brakes', 'ECU Maps', 'Fuel Systems', 'Wheels & Tires'
  ]

  return (
    <div className="min-h-screen pt-20">
      <section className="py-20">
        <div className="container mx-auto px-6">
          <motion.div
            className="glass-card p-8 mb-12"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <h2 className="text-3xl font-orbitron font-bold text-performance-blue mb-6">
              Vehicle Selector
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {['Manufacturer', 'Model', 'Generation', 'Engine', 'Transmission', 'Drivetrain'].map((field) => (
                <select
                  key={field}
                  className="w-full p-3 rounded-xl bg-dark-blue/50 border border-metallic-bronze/30 text-light-cream"
                >
                  <option>{field} - Select</option>
                </select>
              ))}
            </div>
          </motion.div>

          <motion.div
            className="glass-card p-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h2 className="text-3xl font-orbitron font-bold text-performance-blue mb-6">
              My Vehicles
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {vehicles.map((vehicle) => (
                <motion.div
                  key={vehicle.id}
                  className="glass-card p-6 text-center group"
                  whileHover={{ y: -5 }}
                >
                  <div className="w-full h-32 bg-dark-blue/50 rounded-lg mb-4 flex items-center justify-center">
                    <span className="text-sand-beige/50">{vehicle.img}</span>
                  </div>
                  <h3 className="text-xl font-bold text-light-cream">{vehicle.name}</h3>
                  <p className="text-sand-beige/60">{vehicle.year} • {vehicle.hp} HP</p>
                  <Link
                    to={`/garage/${vehicle.id}`}
                    className="inline-block mt-3 text-sm text-performance-blue hover:text-metallic-bronze transition-colors"
                  >
                    Configure
                  </Link>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}