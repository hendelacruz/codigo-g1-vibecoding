// Simple test to verify normalizeRole function
const ROLE_MAPPING = {
  'administrador': 'Administradores',
  'supervisor': 'Supervisores', 
  'tecnico': 'Técnicos',
  'operador': 'Operadores',
  'admin': 'Administradores',
  'tech': 'Técnicos',
  'op': 'Operadores',
  'Administradores': 'Administradores',
  'Supervisores': 'Supervisores',
  'Técnicos': 'Técnicos',
  'Operadores': 'Operadores'
};

const normalizeRole = (role) => {
  return ROLE_MAPPING[role] || role;
};

console.log('Testing normalizeRole function:');
console.log('administrador ->', normalizeRole('administrador'));
console.log('admin ->', normalizeRole('admin'));
console.log('supervisor ->', normalizeRole('supervisor'));
console.log('tecnico ->', normalizeRole('tecnico'));
console.log('tech ->', normalizeRole('tech'));
console.log('operador ->', normalizeRole('operador'));
console.log('op ->', normalizeRole('op'));
console.log('Administradores ->', normalizeRole('Administradores'));

// Test if all expected mappings work
const tests = [
  { input: 'administrador', expected: 'Administradores' },
  { input: 'admin', expected: 'Administradores' },
  { input: 'supervisor', expected: 'Supervisores' },
  { input: 'tecnico', expected: 'Técnicos' },
  { input: 'tech', expected: 'Técnicos' },
  { input: 'operador', expected: 'Operadores' },
  { input: 'op', expected: 'Operadores' },
  { input: 'Administradores', expected: 'Administradores' }
];

let allPassed = true;
tests.forEach(test => {
  const result = normalizeRole(test.input);
  const passed = result === test.expected;
  console.log(`${test.input} -> ${result} (expected: ${test.expected}) ${passed ? '✓' : '✗'}`);
  if (!passed) allPassed = false;
});

console.log(`\nAll tests passed: ${allPassed}`);