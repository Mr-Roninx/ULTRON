import { db, initDatabase } from '../src/db/database.js';

export function resetDatabase(): void {
  console.log('🔄 Resetting ULTRON database to empty clean state...');

  // Disable foreign keys temporarily for clean cascade drops
  db.exec(`
    PRAGMA foreign_keys = OFF;
    DROP TABLE IF EXISTS authority_checks;
    DROP TABLE IF EXISTS execution_records;
    DROP TABLE IF EXISTS ledger_entries;
    DROP TABLE IF EXISTS scores;
    DROP TABLE IF EXISTS allocation_decisions;
    DROP TABLE IF EXISTS recovery_opportunities;
    DROP TABLE IF EXISTS customers;
    PRAGMA foreign_keys = ON;
  `);

  // Recreate all tables
  initDatabase();

  const tables = db.prepare(`
    SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'
  `).all() as { name: string }[];

  console.log('✅ Clean database schema initialized with tables:', tables.map((t) => t.name).join(', '));
  
  const countOpps = (db.prepare('SELECT COUNT(*) as c FROM recovery_opportunities').get() as { c: number }).c;
  console.log(`📊 Total opportunities in reset DB: ${countOpps}`);
}

// Run directly
resetDatabase();
