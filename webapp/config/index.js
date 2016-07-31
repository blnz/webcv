// configuration data for all modes, stubbed for now
var config = {
  local: {
    mode: 'local',
    port: 3000
  },
  staging: {
    mode: 'staging',
    port: 3000
  },
  production: {
    mode: 'production',
    port: 3000
  }
}

// retruns configuration for the named mode. if none provided tries the command argument

module.exports = function(mode) {
  // return the congiguration as requested by "mode" argument, or
  // failing that, on the command line, or
  // fall back to local
  return config[mode || process.argv[2] || 'local'] || config.local;
}
