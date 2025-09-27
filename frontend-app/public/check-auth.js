// Script simple para verificar autenticación
console.log('=== VERIFICACIÓN DE AUTENTICACIÓN ===');

// 1. Verificar Redux Store
if (window.__REDUX_DEVTOOLS_EXTENSION__) {
  console.log('Redux DevTools disponible');
}

// 2. Verificar localStorage
console.log('=== LOCAL STORAGE ===');
const persistRoot = localStorage.getItem('persist:root');
if (persistRoot) {
  try {
    const parsed = JSON.parse(persistRoot);
    console.log('persist:root encontrado:', parsed);
    
    if (parsed.auth) {
      const authState = JSON.parse(parsed.auth);
      console.log('Estado de auth:', authState);
      console.log('Token presente:', !!authState.token);
      console.log('Usuario autenticado:', authState.isAuthenticated);
      console.log('Usuario:', authState.user);
    }
  } catch (e) {
    console.error('Error parseando persist:root:', e);
  }
} else {
  console.log('No se encontró persist:root en localStorage');
}

// 3. Verificar tokens individuales
console.log('=== TOKENS INDIVIDUALES ===');
const accessToken = localStorage.getItem('access_token');
const refreshToken = localStorage.getItem('refresh_token');
console.log('access_token:', accessToken ? 'Presente' : 'No encontrado');
console.log('refresh_token:', refreshToken ? 'Presente' : 'No encontrado');

// 4. Verificar todas las claves de localStorage
console.log('=== TODAS LAS CLAVES DE LOCALSTORAGE ===');
for (let i = 0; i < localStorage.length; i++) {
  const key = localStorage.key(i);
  console.log(`${key}:`, localStorage.getItem(key));
}

// 5. Función para hacer una petición de prueba
window.testAuthAPI = async function() {
  console.log('=== PRUEBA DE API ===');
  try {
    const response = await fetch('http://127.0.0.1:8000/api/auth/users/', {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('Status:', response.status);
    console.log('Headers:', Object.fromEntries(response.headers.entries()));
    
    if (response.ok) {
      const data = await response.json();
      console.log('Datos recibidos:', data);
    } else {
      const errorText = await response.text();
      console.log('Error response:', errorText);
    }
  } catch (error) {
    console.error('Error en la petición:', error);
  }
};

console.log('=== COMANDOS DISPONIBLES ===');
console.log('- testAuthAPI(): Prueba la API con el token actual');
console.log('- localStorage: Acceso directo al localStorage');