import { describe, it, expect } from 'vitest';
import en from '../i18n/en.json';
import hi from '../i18n/hi.json';
import { PRESET_USERS } from '../context/AuthContext';

describe('i18n Translation Dictionaries', () => {
  it('has consistent primary keys in English and Hindi', () => {
    expect(en.app.title).toBe('Swasthya Records');
    expect(hi.app.title).toContain('Swasthya Records');
    expect(en.nav.dashboard).toBeDefined();
    expect(hi.nav.dashboard).toBeDefined();
    expect(en.severity.critical).toBe('URGENT');
    expect(hi.severity.critical).toBe('अति गंभीर');
  });
});

describe('AuthContext Presets', () => {
  it('defines valid ADMIN, STATE_OPERATOR, and DISTRICT_OPERATOR users', () => {
    expect(PRESET_USERS.ADMIN.role).toBe('ADMIN');
    expect(PRESET_USERS.STATE_OPERATOR.role).toBe('STATE_OPERATOR');
    expect(PRESET_USERS.DISTRICT_OPERATOR.role).toBe('DISTRICT_OPERATOR');
  });
});
