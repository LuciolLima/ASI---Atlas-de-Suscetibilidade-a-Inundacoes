import { createRoot } from 'react-dom/client'
import AsiMap from './AsiMap'

// Extend Window interface for our custom properties
declare global {
  interface Window {
    __ASI_MAP_PROPS__: any
    __ASI_MAP_RELOAD__: () => void
    sendToStreamlit: (type: string, value: any) => void
  }
}

// ── Render ───────────────────────────────────────────────────────────────────
const container = document.getElementById('root')!
const root = createRoot(container)

function render() {
  const currentProps = window.__ASI_MAP_PROPS__ || {
    initialViewState: { longitude: -35.03, latitude: -8.28, zoom: 13 },
  }

  root.render(
    <AsiMap
      {...currentProps}
      onClick={(info) => window.sendToStreamlit('click', info)}
      onBoxSelect={(bbox) => window.sendToStreamlit('boxSelect', bbox)}
      onViewStateChange={(vs) => window.sendToStreamlit('viewStateChange', vs)}
    />
  )
}

// Initial render
render()

// Hot reload via Streamlit message
window.__ASI_MAP_RELOAD__ = render

// Listen for Streamlit prop updates
window.addEventListener('message', (event) => {
  if (event.data?.type === 'streamlit:setComponentValue') {
    window.__ASI_MAP_PROPS__ = event.data.value
    render()
  }
})

// Bridge para enviar eventos de volta pro Streamlit
window.sendToStreamlit = (type: string, value: any) => {
  window.parent.postMessage({
    type: 'streamlit:setComponentValue',
    value: { type, value, source: 'asi-map' }
  }, '*')
}