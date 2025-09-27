# Fase 1 - Pruebas Manuales de Autenticación

## Pre-requisitos
- Backend Django ejecutándose en puerto 8000
- Frontend ejecutándose en puerto 3000
- Usuario de prueba creado en Django

## Pruebas a Realizar

### 1. Configuración Inicial ✅
- [ ] `npm run dev` inicia sin errores
- [ ] Aplicación carga en http://localhost:3000
- [ ] Redux DevTools funciona correctamente
- [ ] Persistencia funciona (refresh mantiene estado)

### 2. Autenticación - Login ✅
- [ ] Navegar a /login muestra formulario
- [ ] Validación de campos vacíos funciona
- [ ] Login con credenciales incorrectas muestra error
- [ ] Login con credenciales correctas:
  - [ ] Redirige a /dashboard
  - [ ] Token se guarda en Redux store
  - [ ] Usuario se guarda en Redux store
  - [ ] Estado persiste después de refresh

### 3. Autenticación - Logout ✅
- [ ] Botón logout en dashboard funciona
- [ ] Limpia estado de Redux
- [ ] Redirige a /login
- [ ] Estado limpio persiste después de refresh

### 4. Rutas Protegidas ✅
- [ ] Acceso directo a /dashboard sin auth redirige a /login
- [ ] Después de login, acceso a /dashboard funciona
- [ ] Refresh en /dashboard mantiene sesión

### 5. Token Refresh ✅
- [ ] Token expira y se renueva automáticamente
- [ ] Requests continúan funcionando después de refresh
- [ ] Si refresh falla, redirige a login

### 6. Manejo de Errores ✅
- [x] Errores de red se muestran correctamente
- [x] Errores de autenticación se manejan
- [x] Loading states funcionan
- [x] Panel de pruebas de errores implementado en Dashboard

## Comandos de Prueba

```bash
# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev

# Ejecutar tests unitarios
npm run test

# Build para producción
npm run build
```

## Credenciales de Prueba

**Usuario de prueba:**
- Username: `Hdelacruz`
- Password: `Hygcompe2025`

## Pasos Detallados de Prueba

### Paso 1: Verificar Configuración
1. Abrir terminal en el directorio del proyecto
2. Ejecutar `npm run dev`
3. Verificar que no hay errores en consola
4. Abrir http://localhost:3000 en el navegador
5. Abrir Redux DevTools y verificar que funciona

### Paso 2: Probar Login
1. Navegar a http://localhost:3000/login
2. Intentar enviar formulario vacío (debe mostrar errores de validación)
3. Ingresar credenciales incorrectas (debe mostrar error)
4. Ingresar credenciales correctas:
   - Username: `Hdelacruz`
   - Password: `Hygcompe2025`
5. Verificar redirección a /dashboard
6. Verificar en Redux DevTools que el token y usuario están guardados

### Paso 3: Probar Persistencia
1. Con sesión activa, hacer refresh de la página
2. Verificar que la sesión se mantiene
3. Verificar que el usuario sigue en /dashboard

### Paso 4: Probar Logout
1. En /dashboard, hacer click en logout
2. Verificar redirección a /login
3. Verificar en Redux DevTools que el estado se limpió
4. Hacer refresh y verificar que sigue en /login

### Paso 5: Probar Rutas Protegidas
1. Sin estar logueado, intentar acceder directamente a /dashboard
2. Verificar redirección automática a /login
3. Loguearse y verificar acceso a /dashboard

### Paso 6: Verificar Manejo de Errores
#### Método Manual:
1. Desconectar internet y intentar login
2. Verificar que se muestra error de conexión
3. Reconectar y verificar que funciona normalmente

#### Panel de Pruebas Automatizado:
1. En el Dashboard, localizar el panel "🧪 Pruebas de Manejo de Errores"
2. Observar el estado actual del sistema (Loading, Autenticado, Error)
3. Ejecutar pruebas individuales:
   - **🌐 Test Error de Red**: Simula problemas de conectividad
   - **🔐 Test Error Auth**: Prueba credenciales incorrectas
   - **⏳ Test Loading**: Verifica estados de carga
   - **📡 Test API Errors**: Prueba errores de endpoints
4. O ejecutar **🚀 Ejecutar Todas las Pruebas** para un test completo
5. Revisar los resultados en la consola del panel
6. Verificar que todos los errores se manejan correctamente

## Resultados Esperados

✅ **Todas las pruebas deben pasar**
✅ **No debe haber errores en consola**
✅ **La aplicación debe ser responsive**
✅ **Los estados de loading deben funcionar**
✅ **La persistencia debe mantener la sesión**

## Notas Adicionales

- Verificar que el backend Django esté ejecutándose en puerto 8000
- Asegurarse de que el usuario de prueba existe en la base de datos
- Revisar la consola del navegador para cualquier error JavaScript
- Verificar que las requests HTTP se hacen correctamente usando Network tab