import { Routes, Route, BrowserRouter } from 'react-router-dom'
import { Navigation } from './components/Navigation'
import { HomePage } from './pages/HomePage'
import { FeaturesPage } from './pages/FeaturesPage'
import { GaragePage } from './pages/GaragePage'
// import { SimulatorPage } from './pages/SimulatorPage'
// import { RecommendationsPage } from './pages/RecommendationsPage'
// import { MarketplacePage } from './pages/MarketplacePage'
// import { PricingPage } from './pages/PricingPage'
// import { ContactPage } from './pages/ContactPage'

function App() {
  return (
    <BrowserRouter>
      <Navigation />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/features" element={<FeaturesPage />} />
        <Route path="/garage" element={<GaragePage />} />
        {/* <Route path="/simulator" element={<SimulatorPage />} /> */}
        {/* <Route path="/recommendations" element={<RecommendationsPage />} /> */}
        {/* <Route path="/marketplace" element={<MarketplacePage />} /> */}
        {/* <Route path="/pricing" element={<PricingPage />} /> */}
        {/* <Route path="/contact" element={<ContactPage />} /> */}
      </Routes>
    </BrowserRouter>
  )
}

export default App