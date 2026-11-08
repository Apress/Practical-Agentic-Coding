/**
 * Jest configuration for MoneyMind.
 *
 * The project rules in .agents/rules/project-rules.md mandate Jest, so this
 * config exists to make `npm test` work from a clean clone. It uses ts-jest so
 * tests are TypeScript, and maps the `@/` alias to match tsconfig.json.
 *
 * Tests live in src/**\/*.test.ts. The component tests you add in the lab
 * (WasteCard, TransactionList) need a DOM, so switch testEnvironment to
 * 'jsdom' and add jest-environment-jsdom plus @testing-library/react when you
 * get there. The node environment below covers the schema and flow-mapping
 * tests that ship here.
 */

/** @type {import('jest').Config} */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/*.test.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  // The Next.js app directory and generated output are not unit-test targets.
  testPathIgnorePatterns: ['/node_modules/', '/.next/'],
};
