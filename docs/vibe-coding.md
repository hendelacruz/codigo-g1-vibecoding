# 🎯 Introducción al Vibe Coding con IA (Nivel Principiante)

**Conocimientos previos:** HTML, CSS, JavaScript básico

---

## 🎪 **¿Qué es Vibe Coding?**

El **Vibe Coding** es una metodología donde **colaboras con la IA** para programar más rápido y mejor. En lugar de escribir todo el código desde cero, le "pides" a la IA que te ayude y luego tú mejoras y personalizas el resultado.

### **🧠 Mentalidad Vibe Coding:**

- **IA como compañero:** No reemplaza al programador, lo potencia
- **Iteración rápida:** Prototipo → Test → Mejora → Repite
- **Aprendizaje acelerado:** La IA te enseña patrones y mejores prácticas
- **Foco en la creatividad:** Más tiempo para diseñar, menos tiempo escribiendo código repetitivo

---

### **🎯 BLOQUE 1: Fundamentos y Setup**

#### **Parte 1.1: Introducción al Vibe Coding**

**Objetivo:** Entender la filosofía y configurar el entorno

**Conceptos clave:**

- ¿Qué es la programación asistida por IA?
- Diferencia entre copiar código y colaborar con IA
- Configuración básica de Trae para principiantes

**Demostración en vivo:**

```
"Hola Trae, ayúdame a crear un botón que cambie de color cuando paso el mouse"
```

#### **Parte 1.2: Primeros pasos con React**

**Objetivo:** Entender qué es React sin complicarse

**React explicado simple:**

- React = Forma moderna de crear páginas web interactivas
- Componente = Pieza reutilizable de una página (como un botón)
- JSX = HTML dentro de JavaScript (¡es más fácil de lo que suena!)

**Ejercicio guiado:**
Crear un componente "Saludo" que muestre "¡Hola [nombre]!"

---

### **🎯 BLOQUE 2: IA para Mejorar Código Existente (60 min)**

#### **Parte 2.1: Refactorización Simple (30 min)**

**Objetivo:** Aprender a mejorar código con ayuda de IA

**Conceptos básicos:**

- **Refactorizar** = Mejorar código sin cambiar lo que hace
- **Código limpio** = Fácil de leer y entender
- **Comentarios** = Explicaciones para humanos

**Ejercicio práctico:**
Tomar este código "feo" y mejorarlo con IA:

```javascript
// ❌ CÓDIGO "FEO" (difícil de entender)
function btn() {
  var x = document.getElementById("btn1");
  if (x.style.background == "red") {
    x.style.background = "blue";
  } else {
    x.style.background = "red";
  }
}
```

**Prompt para IA:**

```
"Mejora este código JavaScript para que sea más fácil de entender.
Añade comentarios y usa nombres descriptivos para las variables."
```

#### **Parte 2.2: Documentación Automática**

**Objetivo:** Aprender a documentar código con IA

**¿Por qué documentar?**

- Para recordar qué hace tu código en el futuro
- Para que otros programadores entiendan tu trabajo
- Para demostrar profesionalismo

**Ejercicio:** Pedirle a la IA que explique qué hace cada parte del código

---

### **☕ DESCANSO (15 min)**

---

### **🎯 BLOQUE 3: Creando una Landing Page con IA**

#### **Parte 3.1: Diseño con IA**

**Objetivo:** Generar ideas de diseño usando IA

**Conceptos de diseño web:**

- **Landing page** = Página de aterrizaje (primera impresión)
- **Header** = Parte superior (logo, menú)
- **Hero** = Sección principal con mensaje clave
- **Footer** = Parte inferior (enlaces, contacto)

**Ejercicio grupal:**
Cada estudiante pide a la IA un diseño diferente para una app ficticia

**Prompt ejemplo:**

```
"Diseña una landing page para una app de recetas de cocina.
Que sea colorida y amigable. Incluye: título principal,
3 características principales, y un botón para descargar la app."
```

#### **Parte 3.2: Construyendo la Landing Page**

**Objetivo:** Convertir el diseño en código real

**Estructura básica explicada:**

```html
<!-- Estructura mental de una landing page -->
<header>Logo + Menú</header>
<main>
  <section>Título principal + Botón</section>
  <section>Características</section>
  <section>Testimonios</section>
</main>
<footer>Enlaces + Contacto</footer>
```

**Ejercicio paso a paso:**

1. Crear la estructura HTML básica
2. Añadir estilos con Tailwind CSS
3. Agregar interactividad básica con JavaScript
4. Hacer que se vea bien en móviles

---

### **🎯 BLOQUE 4: Interactividad y Testing Básico**

#### **Parte 4.1: Añadiendo Vida a la Página**

**Objetivo:** Hacer que la página responda a los usuarios

**Interactividad básica:**

- **Clicks en botones** → Algo sucede
- **Hover (pasar mouse)** → Elementos cambian
- **Formularios** → Capturar información del usuario

**Ejercicio:** Añadir un formulario de contacto que funcione

**Prompt para IA:**

```
"Crea un formulario de contacto simple con nombre, email y mensaje.
Cuando el usuario envíe el formulario, muestra un mensaje de 'Gracias'.
Hazlo bonito con Tailwind CSS."
```

#### **Parte 4.2: Testing para Principiantes**

**Objetivo:** Verificar que nuestro código funciona

**¿Qué es testing?**

- **Test** = Prueba automática que verifica si algo funciona
- **Por qué testear** = Evitar errores, ganar confianza
- **Testing con IA** = La IA nos ayuda a escribir las pruebas

**Ejercicio simple:**
Crear un test que verifique si aparece el título de nuestra landing page

**Prompt para IA:**

```
"Ayúdame a crear un test simple que verifique si mi página
tiene un título que dice 'Bienvenido a mi App'.
Explícame paso a paso qué hace cada línea."
```

---

## 🛠️ **Herramientas Simplificadas**

### **Lo que vamos a usar:**

- **Trae** → Editor inteligente (nuestra IA amiga)
- **HTML** → Estructura de la página
- **CSS (Tailwind)** → Hacer que se vea bonito
- **JavaScript** → Hacer que sea interactivo
- **React** → Organizar mejor nuestro código

### **Lo que NO necesitas saber aún:**

- TypeScript (lo usaremos básico)
- Configuraciones complejas
- Patrones avanzados de React
- Testing complejo

---

## 📝 **Ejercicios Prácticos Adaptados**

### **🔧 Ejercicio 1: Mi Primer Componente React**

**Nivel:** Muy básico

```javascript
// Vamos a entender este código juntos:

function MiPrimerBoton() {
  // Esta es una función que retorna HTML
  return (
    <button className="bg-blue-500 text-white px-4 py-2 rounded">
      ¡Haz click aquí!
    </button>
  );
}

// ¿Qué hace cada parte?
// - function = declaramos una función
// - return = lo que va a mostrar en la página
// - className = clases CSS (en React se llama className, no class)
// - bg-blue-500 = fondo azul (Tailwind CSS)
```

**Tu turno:** Pídele a la IA que cree un botón diferente

**Prompt sugerido:**

```
"Crea un botón verde que diga 'Enviar' y que sea grande.
Usa Tailwind CSS y explícame qué hace cada clase."
```

### **🎨 Ejercicio 2: Página Personal Simple (40 min)**

**Nivel:** Básico

**Objetivo:** Crear una mini landing page personal

**Estructura sugerida:**

1. **Header:** Tu nombre como título grande
2. **Sobre mí:** Párrafo corto sobre ti
3. **Habilidades:** Lista de 3 cosas que sabes hacer
4. **Contacto:** Botón que diga "Contáctame"

**Prompt para empezar:**

```
"Ayúdame a crear una página personal simple. Debe tener:
- Un título grande con mi nombre
- Una sección sobre mí
- Una lista de mis habilidades
- Un botón de contacto
Hazlo con React y Tailwind CSS. Explícame cada parte."
```

### **🧪 Ejercicio 3: Mi Primer Test (15 min)**

**Nivel:** Muy básico

**Objetivo:** Entender qué es un test sin complicarse

```javascript
// Test súper simple explicado:

test("mi página tiene un título", () => {
  // 1. Renderizar (mostrar) mi componente
  render(<MiPagina />);

  // 2. Buscar el título en la página
  const titulo = screen.getByText("Mi Nombre");

  // 3. Verificar que existe
  expect(titulo).toBeInTheDocument();
});

// En español:
// "Verifica que mi página tenga un elemento que diga 'Mi Nombre'"
```

**Tu turno:** Pídele a la IA que cree un test para tu botón

---

## 🎓 **Metodología de Enseñanza Adaptada**

### **1. Explicación Visual**

- Profesor muestra en pantalla grande
- Analogías con cosas cotidianas
- Preguntas frecuentes: "¿Qué pasaría si...?"

### **2. Práctica Guiada (20 min por ejercicio)**

- Todos hacemos lo mismo al mismo tiempo
- Profesor va revisando pantallas individuales
- Pausa para preguntas cada 5 minutos

### **3. Experimentación Libre**

- "Ahora prueben cambiar esto..."
- Estudiantes personalizan su código
- Compartir descubrimientos con el grupo

### **4. Show & Tell**

- 2-3 estudiantes muestran lo que hicieron
- Celebrar los experimentos, no solo los "correctos"
- Aprender de los errores juntos

---

## ✅ **Evaluación Simplificada**

### **Entregable:** Página personal simple que tenga:

- ✅ Tu nombre como título
- ✅ Al menos 2 secciones (sobre mí, habilidades, etc.)
- ✅ Un botón que haga algo (cambiar color, mostrar mensaje, etc.)
- ✅ Se vea bien en móvil
- ✅ Al menos un test que funcione

### **Criterios:**

1. **¿Funciona?** (40%) - La página se carga y no tiene errores
2. **¿Se ve bien?** (30%) - Diseño ordenado y responsive
3. **¿Es personal?** (20%) - Refleja la personalidad del estudiante
4. **¿Experimentaste?** (10%) - Probaste cosas nuevas más allá del ejercicio base

**No evaluamos:**

- Código perfecto (¡estamos aprendiendo!)
- Complejidad técnica
- Conocimiento memorizado

---

## 💡 **Prompts Especiales para Principiantes**

### **🤝 Para pedir ayuda a la IA:**

```
"Soy principiante en programación. Ayúdame a [tarea específica].
Por favor explícame paso a paso qué hace cada parte del código
y usa términos simples."
```

### **🔍 Para entender código existente:**

```
"¿Puedes explicarme qué hace este código como si fuera un niño de 10 años?
[pegar código aquí]"
```

### **🛠️ Para solucionar errores:**

```
"Tengo este error: [copiar mensaje de error].
Soy principiante, ¿puedes ayudarme a solucionarlo de forma simple?"
```

### **🎨 Para mejorar el diseño:**

```
"Mi página web se ve muy simple. ¿Puedes darme ideas para que se vea
más profesional pero sin complicar mucho el código?"
```

---

## 📚 **Recursos de Apoyo Simplificados**

### **Cheat Sheets:**

- [Guía visual de HTML básico]
- [Colores y clases más usadas de Tailwind]
- [Estructura básica de un componente React]
- [Prompts útiles para principiantes]

### **Para practicar en casa:**

- Pequeños retos diarios (cambiar un color, añadir un párrafo)
- Videos cortos explicando conceptos (max 5 min cada uno)
- Comunidad de Discord para preguntas
- Ejemplos de código comentado paso a paso

---

## 🚀 **Siguientes Pasos (Tarea Opcional)**

### **Experimentos para la casa:**

1. **Cambiar colores:** Prueba diferentes combinaciones de colores
2. **Añadir imágenes:** Busca fotos tuyas o de internet y añádelas
3. **Más secciones:** Agrega hobbies, metas, proyectos soñados
4. **Hacer preguntas:** En Discord, pregunta "¿Cómo hago para...?"

### **Próxima clase:**

- Más interactividad (formularios que funcionen de verdad)
- Conectar con bases de datos simples
- Trabajar en equipo con Git básico

---

## 💝 **Tips para el Instructor**

### **Antes de la clase:**

- Tener ejemplos funcionando en diferentes niveles
- Preparar analogías simples para conceptos técnicos
- Crear "código de emergencia" para estudiantes que se atrasen

### **Durante la clase:**

- **Ir DESPACIO** - mejor pocas cosas bien entendidas que muchas confusas
- **Celebrar errores** - "¡Excelente error! Aprendamos de él"
- **Usar humor** - programar puede ser divertido
- **Preguntar constantemente** - "¿Alguien se perdió? ¡Es normal!"

### **Señales de que vas muy rápido:**

- Caras de confusión
- Silencio total cuando preguntas
- Muchas manos levantadas al mismo tiempo
- Estudiantes copiando sin entender

### **Frases útiles:**

- "No se preocupen si no entienden todo, vamos paso a paso"
- "El objetivo es experimentar, no ser perfectos"
- "Cada error es una oportunidad de aprender algo nuevo"
- "La IA es nuestra amiga, no tengamos miedo de preguntarle"

---

**¡Que tengan una clase increíble llena de descubrimientos! 🚀✨**

**Recuerda:** El objetivo no es formar expertos en 4 horas, sino despertar la curiosidad y mostrar que programar con IA es accesible y divertido.
