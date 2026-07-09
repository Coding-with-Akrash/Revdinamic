import { motion } from 'framer-motion'
import { Car, Cpu, Gauge, Zap, ShoppingCart, BarChart3 } from 'lucide-react'

export const FeaturesPage = () => {
  const features = [
    {
      icon: Car,
      title: 'Vehicle Configuration',
      description: 'Configure every aspect of your vehicle with precision engineering tools.',
    },
    {
      icon: Cpu,
      title: 'AI Performance Advisor',
      description: 'Receive intelligent upgrade recommendations tailored to your build.',
    },
    {
      icon: Gauge,
      title: 'Virtual Dyno Tuning',
      description: 'Analyze horsepower and torque curves before modifications.',
    },
    {
      icon: Zap,
      title: 'OBD Integration',
      description: 'Connect and monitor live vehicle telemetry in real-time.',
    },
    {
      icon: ShoppingCart,
      title: 'Parts Marketplace',
      description: 'Explore compatible performance upgrades with AI matching.',
    },
    {
      icon: BarChart3,
      title: 'Performance Comparison',
      description: 'Compare stock and modified setups with detailed analytics.',
    },
  ]

  return (
    <div className="min-h-screen pt-20">
      <section className="py-20">
        <div className="container mx-auto px-6">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <h1 className="text-5xl font-orbitron font-bold text-gradient mb-4">
              Features
            </h1>
            <p className="text-sand-beige/70 max-w-2xl mx-auto">
              Advanced AI-driven platform for automotive performance optimization
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                className="glass-card p-8 text-center"
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -10 }}
              >
                <feature.icon className="w-12 h-12 text-performance-blue mx-auto mb-4" />
                <h3 className="text-xl font-bold text-light-cream mb-3">{feature.title}</h3>
                <p className="text-sand-beige/60">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}