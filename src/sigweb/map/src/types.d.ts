// Type declarations for external modules without types
declare module '@deck.gl/react' {
  import { DeckGL } from '@deck.gl/core'
  export { DeckGL }
}

declare module '@deck.gl/mapbox' {
  import { MapboxOverlay } from '@deck.gl/core'
  export { MapboxOverlay }
}

declare module 'maplibre-gl' {
  const maplibregl: any
  export default maplibregl
}

declare module '@deck.gl/layers' {
  export {
    ScatterplotLayer,
    HexagonLayer,
    HeatmapLayer,
    GeoJsonLayer,
    Layer,
  } from '@deck.gl/layers'
}

declare module '@deck.gl/core' {
  export {
    DeckGL,
    Layer,
    ViewState,
    LinearInterpolator,
  } from '@deck.gl/core'
}