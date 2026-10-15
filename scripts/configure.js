#!/usr/bin/env node
'use strict';
/*
 * Turn on the Java Skill Base plugin for a person, a team (repository) or an organisation.
 *
 *   node scripts/configure.js user    [--run] [--repo owner/repo] [--ref branch]
 *   node scripts/configure.js project [dir] [--repo owner/repo] [--ref branch]
 *   node scripts/configure.js managed [--strict] [--out file] [--repo owner/repo] [--ref branch]
 *
 *   user     print (or with --run, execute) the two claude commands that install the plugin for
 *            this user in every project on this machine
 *   project  merge the marketplace + enabledPlugins entries into <dir>/.claude/settings.json
 *            (commit it so every contributor is prompted to install the plugin)
 *   managed  print the managed-settings policy that force-enables the plugin for an organisation
 *            (--strict also allow-lists the marketplace sources); --out writes it to a file
 *
 * Only Node.js is required. Nothing is overwritten: existing settings keys are preserved.
 */
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const DEFAULT_REPO = 'getdipakkumar2008-coder/SKillforJAVA';
const MARKETPLACE = 'java-skill-base';
const PLUGIN = 'java-skills';

function parseArgs(argv) {
  const opts = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--run' || a === '--strict') opts[a.slice(2)] = true;
    else if (a === '--repo' || a === '--ref' || a === '--out') opts[a.slice(2)] = argv[++i];
    else if (a.startsWith('--')) { console.error('unknown option: ' + a); process.exit(2); }
    else opts._.push(a);
  }
  return opts;
}

function marketplaceEntry(opts, withAuto) {
  const source = { source: 'github', repo: opts.repo || DEFAULT_REPO };
  if (opts.ref) source.ref = opts.ref;
  const entry = { source };
  if (withAuto) entry.autoUpdate = true;
  return entry;
}

function deepMerge(target, extra) {
  for (const [k, v] of Object.entries(extra)) {
    if (v && typeof v === 'object' && !Array.isArray(v)) {
      target[k] = deepMerge(target[k] && typeof target[k] === 'object' && !Array.isArray(target[k]) ? target[k] : {}, v);
    } else {
      target[k] = v;
    }
  }
  return target;
}

function projectSettings(opts) {
  return {
    extraKnownMarketplaces: { [MARKETPLACE]: marketplaceEntry(opts, false) },
    enabledPlugins: { [`${PLUGIN}@${MARKETPLACE}`]: true }
  };
}

function managedSettings(opts) {
  const repo = opts.repo || DEFAULT_REPO;
  const base = {
    extraKnownMarketplaces: { [MARKETPLACE]: marketplaceEntry(opts, true) },
    enabledPlugins: { [`${PLUGIN}@${MARKETPLACE}`]: true }
  };
  if (!opts.strict) return base;
  const strict = {
    strictKnownMarketplaces: [
      { source: 'github', repo },
      { source: 'github', repo: 'anthropics/claude-plugins-official' },
      { source: 'skills-dir' }
    ]
  };
  strict.extraKnownMarketplaces = {
    ...base.extraKnownMarketplaces,
    'claude-plugins-official': { source: { source: 'github', repo: 'anthropics/claude-plugins-official' } }
  };
  strict.enabledPlugins = base.enabledPlugins;
  return strict;
}

function cmdUser(opts) {
  const repo = opts.repo || DEFAULT_REPO;
  const add = ['plugin', 'marketplace', 'add', opts.ref ? `${repo}#${opts.ref}` : repo];
  const install = ['plugin', 'install', `${PLUGIN}@${MARKETPLACE}`, '--scope', 'user'];
  console.log('claude ' + add.join(' '));
  console.log('claude ' + install.join(' '));
  if (!opts.run) { console.log('\n(run these yourself, or pass --run to execute them)'); return 0; }
  for (const args of [add, install]) {
    const r = spawnSync('claude', args, { stdio: 'inherit', shell: process.platform === 'win32' });
    if (r.status !== 0) { console.error('command failed: claude ' + args.join(' ')); return r.status || 1; }
  }
  console.log('\nDone. Start a new Claude Code session in any Java project; /plugin shows java-skills as installed.');
  return 0;
}

function cmdProject(opts) {
  const dir = path.resolve(opts._[1] || '.');
  if (!fs.existsSync(dir)) { console.error('no such directory: ' + dir); return 2; }
  const file = path.join(dir, '.claude', 'settings.json');
  let current = {};
  if (fs.existsSync(file)) {
    try { current = JSON.parse(fs.readFileSync(file, 'utf8')); }
    catch (e) { console.error(`cannot parse ${file} (${e.message}); fix or merge it by hand with templates/project-settings.json`); return 2; }
  }
  const merged = deepMerge(current, projectSettings(opts));
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(merged, null, 2) + '\n', 'utf8');
  console.log('updated ' + file);
  console.log('Commit it. Each contributor is asked to trust the folder and install the plugin the first time they open the project in Claude Code.');
  return 0;
}

function cmdManaged(opts) {
  const json = JSON.stringify(managedSettings(opts), null, 2) + '\n';
  if (opts.out) {
    fs.mkdirSync(path.dirname(path.resolve(opts.out)), { recursive: true });
    fs.writeFileSync(opts.out, json, 'utf8');
    console.log('wrote ' + opts.out);
  } else {
    process.stdout.write(json);
  }
  console.error([
    '',
    'Deploy this as managed settings (it cannot be overridden by users):',
    '  macOS          /Library/Application Support/ClaudeCode/managed-settings.json',
    '  Linux and WSL  /etc/claude-code/managed-settings.json',
    '  Windows        C:\\Program Files\\ClaudeCode\\managed-settings.json',
    '  or via MDM (macOS profile com.anthropic.claudecode; Windows HKLM\\SOFTWARE\\Policies\\ClaudeCode value "Settings"),',
    '  or paste into Organization settings > Claude Code > Managed settings in the claude.ai admin console.',
    '(Paths from the Claude Code managed-settings documentation; verify them for your Claude Code version.)'
  ].join('\n'));
  return 0;
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  const cmd = opts._[0];
  const table = { user: cmdUser, project: cmdProject, managed: cmdManaged };
  if (!table[cmd]) {
    console.error('usage: node scripts/configure.js <user|project|managed> [options]   (see the header of this file)');
    process.exit(2);
  }
  process.exit(table[cmd](opts));
}

main();
