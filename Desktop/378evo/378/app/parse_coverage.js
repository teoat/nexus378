const fs = require('fs');

const coverage = JSON.parse(fs.readFileSync('coverage/coverage-final.json', 'utf-8'));

for (const file in coverage) {
  const { statements, branches, functions } = coverage[file];
  if (statements && branches && functions && (statements.pct < 100 || branches.pct < 100 || functions.pct < 100)) {
    console.log(`${file}:`);
    console.log(`  Statements: ${statements.pct}%`);
    console.log(`  Branches: ${branches.pct}%`);
    console.log(`  Functions: ${functions.pct}%`);
  }
}