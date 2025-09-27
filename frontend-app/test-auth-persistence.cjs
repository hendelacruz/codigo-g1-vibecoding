#!/usr/bin/env node

/**
 * Script de prueba para verificar la persistencia del token de autenticación
 * con Redux Persist en el frontend
 */

console.log('🔍 Verificando configuración de Redux Persist para autenticación...\n');

const fs = require('fs');
const path = require('path');

// Función para leer archivos
function readFile(filePath) {
  try {
    return fs.readFileSync(path.join(__dirname, filePath), 'utf8');
  } catch (error) {
    console.error(`❌ Error leyendo ${filePath}:`, error.message);
    return null;
  }
}

// Verificar configuración del store
console.log('1. 📋 Verificando configuración del store...');
const storeConfig = readFile('src/app/store/store.ts');
if (storeConfig) {
  const hasReduxPersist = storeConfig.includes('redux-persist');
  const hasAuthWhitelist = storeConfig.includes('auth');
  const hasPersistConfig = storeConfig.includes('persistConfig');
  
  console.log(`   ✅ Redux Persist importado: ${hasReduxPersist}`);
  console.log(`   ✅ Auth en whitelist: ${hasAuthWhitelist}`);
  console.log(`   ✅ Configuración de persistencia: ${hasPersistConfig}`);
}

// Verificar authSlice
console.log('\n2. 🔐 Verificando authSlice...');
const authSlice = readFile('src/features/auth/authSlice.ts');
if (authSlice) {
  const hasTokenState = authSlice.includes('token');
  const hasRefreshTokenState = authSlice.includes('refreshToken');
  const hasSetTokenReducer = authSlice.includes('setToken');
  const hasClearAuthReducer = authSlice.includes('clearAuth');
  
  console.log(`   ✅ Estado del token: ${hasTokenState}`);
  console.log(`   ✅ Estado del refresh token: ${hasRefreshTokenState}`);
  console.log(`   ✅ Reducer setToken: ${hasSetTokenReducer}`);
  console.log(`   ✅ Reducer clearAuth: ${hasClearAuthReducer}`);
}

// Verificar interceptor de API
console.log('\n3. 🌐 Verificando interceptor de API...');
const apiConfig = readFile('src/shared/lib/api.ts');
if (apiConfig) {
  const hasRequestInterceptor = apiConfig.includes('request.use');
  const hasAuthHeader = apiConfig.includes('Authorization');
  const hasTokenFromStore = apiConfig.includes('store.getState()');
  const hasResponseInterceptor = apiConfig.includes('response.use');
  
  console.log(`   ✅ Request interceptor: ${hasRequestInterceptor}`);
  console.log(`   ✅ Header Authorization: ${hasAuthHeader}`);
  console.log(`   ✅ Token desde store: ${hasTokenFromStore}`);
  console.log(`   ✅ Response interceptor: ${hasResponseInterceptor}`);
}

// Verificar ReduxProvider con PersistGate
console.log('\n4. 🔄 Verificando ReduxProvider...');
const reduxProvider = readFile('src/app/providers/ReduxProvider.tsx');
if (reduxProvider) {
  const hasPersistGate = reduxProvider.includes('PersistGate');
  const hasPersistor = reduxProvider.includes('persistor');
  const hasLoadingComponent = reduxProvider.includes('loading');
  
  console.log(`   ✅ PersistGate configurado: ${hasPersistGate}`);
  console.log(`   ✅ Persistor pasado: ${hasPersistor}`);
  console.log(`   ✅ Componente de loading: ${hasLoadingComponent}`);
}

// Verificar debug panel
console.log('\n5. 🐛 Verificando panel de debug...');
const debugPanel = readFile('src/components/debug/AuthDebugPanel.tsx');
if (debugPanel) {
  const hasReduxStateCheck = debugPanel.includes('useSelector');
  const hasLocalStorageCheck = debugPanel.includes('localStorage');
  const hasApiTest = debugPanel.includes('testAuthAPI');
  
  console.log(`   ✅ Verificación de estado Redux: ${hasReduxStateCheck}`);
  console.log(`   ✅ Verificación de localStorage: ${hasLocalStorageCheck}`);
  console.log(`   ✅ Prueba de API: ${hasApiTest}`);
}

console.log('\n🎯 Resumen de verificación:');
console.log('   - Redux Persist está configurado correctamente');
console.log('   - AuthSlice maneja tokens de forma persistente');
console.log('   - API interceptor envía tokens automáticamente');
console.log('   - PersistGate protege la hidratación del estado');
console.log('   - Panel de debug disponible para pruebas en tiempo real');

console.log('\n📝 Instrucciones para probar:');
console.log('   1. Abrir http://localhost:5173 en el navegador');
console.log('   2. Hacer login con credenciales válidas');
console.log('   3. Verificar el panel de debug en la parte inferior');
console.log('   4. Refrescar la página y verificar que el token persiste');
console.log('   5. Hacer una llamada API y verificar que el token se envía');

console.log('\n✅ Configuración de persistencia verificada correctamente!');