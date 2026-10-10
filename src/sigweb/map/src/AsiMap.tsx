import React, { useEffect, useMemo } from 'react'
import { DeckGL } from '@deck.gl/react'
import { ScatterplotLayer, HexagonLayer, HeatmapLayer, GeoJsonLayer } from '@deck.gl/layers'
import './AsiMap.css'

// ── GeoJSON Loader ──────────────────────────────────────────────────────────
const loadGeoJSON = async () => {
  try {
    const [bairros, hidro] = await Promise.all([
      fetch('/data/curated/bairros.geojson').then(r => r.json()),
      fetch('/data/curated/hidro.geojson').then(r => r.json()),
    ])
    ;(window as any).bairrosGeoJSON = bairros
    ;(window as any).hidroGeoJSON = hidro
    if ((window as any).__ASI_MAP_RELOAD__) (window as any).__ASI_MAP_RELOAD__()
  } catch (e) {
    console.warn('GeoJSON externo não carregado:', e)
  }
}

// ── Props Types ──────────────────────────────────────────────────────────────
interface AsiMapProps {
  data?: string
  dataFormat?: 'arrow' | 'geojson'
  initialViewState?: {
    longitude: number
    latitude: number
    zoom: number
    pitch?: number
    bearing?: number
  }
  highlightPoint?: { lat: number; lon: number } | null
  layers?: {
    points?: boolean
    hexagon?: boolean
    heatmap?: boolean
    bairros?: boolean
    hidro?: boolean
  }
  mapStyle?: 'dark' | 'light' | 'satellite' | 'osm'
  onClick?: (info: ClickInfo) => void
  onBoxSelect?: (bbox: [number, number, number, number]) => void
  onViewStateChange?: (viewState: ViewState) => void
}

interface ClickInfo {
  lat: number
  lon: number
  twi?: number
  classe?: string
  bairro?: string
  [key: string]: any
}

interface ViewState {
  longitude: number
  latitude: number
  zoom: number
  pitch: number
  bearing: number
}

// ── Layer Factory ────────────────────────────────────────────────────────────
const createLayers = (props: AsiMapProps, data: any[]) => {
  const layers: any[] = []
  if (!data || data.length === 0) return layers

  // 1. Scatterplot (pontos TWI)
  if (props.layers?.points !== false) {
    layers.push(new ScatterplotLayer({
      id: 'twi-points',
      data,
      getPosition: (d: any) => [d.longitude, d.latitude],
      getRadius: (d: any) => Math.max(3, Math.min(10, d.twi / 2)),
      getFillColor: (d: any) => twiToColor(d.twi),
      getLineColor: [255, 255, 255, 100],
      lineWidthMinPixels: 0.5,
      pickable: true,
      autoHighlight: true,
      highlightColor: [255, 255, 0, 200],
    }))
  }

  // 2. Hexagon (3D agregação)
  if (props.layers?.hexagon) {
    layers.push(new HexagonLayer({
      id: 'twi-hexagon',
      data,
      getPosition: (d: any) => [d.longitude, d.latitude],
      radius: 200,
      elevationScale: 50,
      extruded: true,
      coverage: 0.9,
      getColorWeight: (d: any) => d.twi,
      colorRange: [
        [0, 180, 255, 150],   // baixo
        [255, 255, 0, 180],   // médio
        [255, 100, 0, 200],   // alto
        [200, 0, 0, 220],     // crítico
      ],
    }))
  }

  // 3. Heatmap
  if (props.layers?.heatmap) {
    layers.push(new HeatmapLayer({
      id: 'twi-heatmap',
      data,
      getPosition: (d: any) => [d.longitude, d.latitude],
      getWeight: (d: any) => d.twi / 20,
      radiusPixels: 30,
      intensity: 1,
      threshold: 0.05,
    }))
  }

  // 4. Bairros (GeoJSON)
  if (props.layers?.bairros && (window as any).bairrosGeoJSON) {
    layers.push(new GeoJsonLayer({
      id: 'bairros',
      data: (window as any).bairrosGeoJSON,
      stroked: true,
      filled: false,
      getLineColor: [255, 255, 255, 100],
      getLineWidth: 2,
      pickable: true,
      autoHighlight: true,
    }))
  }

  // 5. Hidrografia
  if (props.layers?.hidro && (window as any).hidroGeoJSON) {
    layers.push(new GeoJsonLayer({
      id: 'hidro',
      data: (window as any).hidroGeoJSON,
      stroked: true,
      filled: false,
      getLineColor: [0, 191, 255, 200],
      getLineWidth: 2,
    }))
  }

  // 6. Highlight point
  if (props.highlightPoint) {
    layers.push(new ScatterplotLayer({
      id: 'highlight',
      data: [props.highlightPoint],
      getPosition: (d: any) => [d.lon, d.lat],
      getRadius: 16,
      getFillColor: [255, 255, 0, 255],
      getLineColor: [0, 0, 0, 255],
      lineWidthMinPixels: 3,
      pickable: false,
    }))
  }

  return layers
}

// ── Color Scale ──────────────────────────────────────────────────────────────
const twiToColor = (twi: number): [number, number, number, number] => {
  if (twi >= 16) return [139, 0, 0, 220]      // CRITICO
  if (twi >= 12) return [255, 69, 0, 220]     // ALTO
  if (twi >= 8) return [255, 215, 0, 220]     // MODERADO
  if (twi >= 4) return [30, 144, 255, 220]    // BAIXO
  return [173, 216, 230, 200]                 // MUITO_BAIXO
}

// ── Main Component ──────────────────────────────────────────────────────────
export const AsiMap: React.FC<AsiMapProps> = (props) => {
  // Parse data once
  const data = useMemo(() => {
    if (!props.data) return []
    try {
      if (props.dataFormat === 'arrow') {
        const bytes = Uint8Array.from(atob(props.data), c => c.charCodeAt(0))
        return JSON.parse(new TextDecoder().decode(bytes))
      }
      return JSON.parse(props.data)
    } catch {
      return []
    }
  }, [props.data, props.dataFormat])

  // Initialize MapLibre GeoJSON
  useEffect(() => {
    loadGeoJSON()
  }, [])

  const layers = useMemo(() => createLayers(props, data), [props, data])

  return (
    <DeckGL
      initialViewState={props.initialViewState || {
        longitude: -35.03,
        latitude: -8.28,
        zoom: 13,
        pitch: 0,
        bearing: 0,
      }}
      controller={true}
      layers={layers}
      onClick={(info: any) => {
        if (info.object && props.onClick) {
          props.onClick({
            lat: info.coordinate[1],
            lon: info.coordinate[0],
            ...info.object,
          })
        }
      }}
      onViewStateChange={(viewState: any) => {
        props.onViewStateChange?.(viewState)
      }}
      style={{ width: '100%', height: '100%' }}
    />
  )
}

export default AsiMap