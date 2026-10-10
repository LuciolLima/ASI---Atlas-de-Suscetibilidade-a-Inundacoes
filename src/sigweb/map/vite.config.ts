import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import string from 'vite-plugin-string'

export default defineConfig({
  plugins: [
    react(),
    string({
      include: ['**/*.html', '**/*.css'],
    }),
  ],
  build: {
    lib: {
      entry: 'src/AsiMap.tsx',
      name: 'AsiMap',
      formats: ['umd'],
      fileName: 'AsiMap',
    },
    rollupOptions: {
      external: ['react', 'react-dom', '@deck.gl/core', '@deck.gl/layers', '@deck.gl/mapbox', 'maplibre-gl'],
      output: {
        globals: {
          react: 'React',
          'react-dom': 'ReactDOM',
          '@deck.gl/core': 'deck',
          '@deck.gl/layers': 'deck',
          '@deck.gl/mapbox': 'deck',
          'maplibre-gl': 'maplibregl',
        },
      },
    },
    outDir: '../../streamlit_components/asi_map',
    emptyOutDir: true,
  },
})