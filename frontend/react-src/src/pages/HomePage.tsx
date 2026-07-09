import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Car, Gauge, Zap, ShoppingCart, BarChart3, Cpu, Wrench } from 'lucide-react'

export const HomePage = () => {
  const stats = [
    { value: '500+', label: 'Supported Vehicles', icon: Car },
    { value: '1200+', label: 'Performance Parts', icon: Wrench },
    { value: '95%', label: 'Prediction Accuracy', icon: Gauge },
    { value: 'Real-Time', label: 'Dyno Analysis', icon: Zap },
  ]

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
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center pt-20">
        <div className="container mx-auto px-6 grid md:grid-cols-2 gap-12 items-center">
          {/* Left Side */}
          <div>
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h1 className="text-5xl md:text-6xl font-orbitron font-bold mb-6">
                <span className="text-gradient">AI-Powered Vehicle Performance Engineering</span>
              </h1>
              <p className="text-xl text-sand-beige/80 mb-8 max-w-lg">
                Configure, Tune, Simulate, and Analyze Your Vehicle Performance in Real Time.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 mb-12">
                <Link
                  to="/garage"
                  className="px-8 py-4 rounded-full bg-gradient-to-r from-performance-blue to-metallic-bronze text-light-cream font-bold text-lg hover:opacity-90 transition-all duration-300 transform hover:scale-105"
                >
                  Start Tuning
                </Link>
                <Link
                  to="/features"
                  className="px-8 py-4 rounded-full border border-metallic-bronze/50 text-sand-beige font-medium text-lg hover:bg-metallic-bronze/10 transition-all duration-300"
                >
                  Explore Features
                </Link>
              </div>

              {/* Stats Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {stats.map((stat, index) => (
                  <motion.div
                    key={stat.label}
                    className="glass-card p-4 text-center"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 + index * 0.1 }}
                  >
                    <stat.icon className="w-6 h-6 text-performance-blue mx-auto mb-2" />
                    <div className="text-2xl font-orbitron font-bold text-light-cream">
                      {stat.value}
                    </div>
                    <div className="text-xs text-sand-beige/60">{stat.label}</div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Right Side - 3D Car Visualization */}
          <div className="relative">
            <motion.div
              className="glass-card p-8 relative overflow-hidden"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1, delay: 0.3 }}
            >
              <svg
                viewBox="0 0 400 200"
                className="w-full h-64"
              >
                <defs>
                  <linearGradient id="carGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#186784" />
                    <stop offset="100%" stopColor="#0C2E3D" />
                  </linearGradient>
                </defs>
                <motion.path
                  d="M50 120 L50 100 Q50 80 80 80 L300 80 Q330 80 330 100 L330 120 Z"
                  fill="url(#carGradient)"
                  stroke="#9A7C65"
                  strokeWidth="2"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ duration: 2 }}
                />
                <motion.path
                  d="M80 100 L120 60 L280 60 L320 100"
                  fill="#0C2E3D"
                  stroke="#DAC6B6"
                  strokeWidth="1"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ duration: 2, delay: 0.5 }}
                />
                <motion.circle
                  cx="110"
                  cy="125"
                  r="20"
                  fill="#9A7C65"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
                />
                <motion.circle
                  cx="290"
                  cy="125"
                  r="20"
                  fill="#9A7C65"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
                />
                <g transform="translate(20,20)">
                  <circle cx="0" cy="0" r="25" fill="#000101" stroke="#186784" strokeWidth="2" />
                  <motion.line
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="-20"
                    stroke="#DAC6B6"
                    strokeWidth="2"
                    animate={{ rotate: -45 }}
                    transition={{ duration: 2 }}
                    style={{ transformOrigin: '0 0' }}
                  />
                  <text x="0" y="5" fontSize="8" fill="#DAC6B6" textAnchor="middle">RPM</text>
                </g>
                <g transform="translate(350,20)">
                  <circle cx="0" cy="0" r="25" fill="#000101" stroke="#9A7C65" strokeWidth="2" />
                  <motion.line
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="-20"
                    stroke="#DAC6B6"
                    strokeWidth="2"
                    animate={{ rotate: 25 }}
                    transition={{ duration: 2, delay: 0.5 }}
                    style={{ transformOrigin: '0 0' }}
                  />
                  <text x="0" y="5" fontSize="8" fill="#DAC6B6" textAnchor="middle">SPD</text>
                </g>
                <motion.text
                  x="200"
                  y="160"
                  fontSize="24"
                  fill="#DAC6B6"
                  textAnchor="middle"
                  animate={{ y: [150, 140, 150], opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 3, repeat: Infinity }}
                >
                  450 HP
                </motion.text>
              </svg>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl font-orbitron font-bold text-gradient mb-4">
              Performance Engineering Tools
            </h2>
            <p className="text-sand-beige/70 max-w-2xl mx-auto">
              Advanced AI-driven platform for automotive performance optimization
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                className="glass-card p-8 text-center group"
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -10 }}
              >
                <feature.icon className="w-12 h-12 text-performance-blue mx-auto mb-4 group-hover:text-metallic-bronze transition-colors" />
                <h3 className="text-xl font-bold text-light-cream mb-3">{feature.title}</h3>
                <p className="text-sand-beige/60 text-sm">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Dyno Simulator Preview */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <motion.div
            className="glass-card p-8"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            <h3 className="text-2xl font-orbitron font-bold text-performance-blue mb-6">
              Dyno Simulator Preview
            </h3>
            <div className="h-64 bg-dark-blue/50 rounded-xl flex items-center justify-center">
              <p className="text-sand-beige/50">Interactive Horsepower & Torque Graph</p>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}