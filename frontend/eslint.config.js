import js from '@eslint/js';
import globals from 'globals';
import hooks from 'eslint-plugin-react-hooks';
import refresh from 'eslint-plugin-react-refresh';
import react from 'eslint-plugin-react';

export default [
  { ignores: ['dist'] },
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: { ecmaVersion: 2022, globals: globals.browser, parserOptions: { ecmaFeatures: { jsx: true }, sourceType: 'module' } },
    plugins: { react, 'react-hooks': hooks, 'react-refresh': refresh },
    rules: { ...js.configs.recommended.rules, ...hooks.configs.recommended.rules, 'react/jsx-uses-vars': 'error', 'no-unused-vars': ['error', { argsIgnorePattern: '^_' }], 'react-refresh/only-export-components': ['warn', { allowConstantExport: true }] },
  },
];
