/* Turbo Pixel Racer — browser port of the Pygame build in car_race_game/.
 * Same rules, constants and 60 FPS feel as the desktop game, on a canvas. */
(function () {
  'use strict';

  /* --------------------------------------------------------------------- */
  /* Constants (mirrors car_race_game/src/constants.py)                     */
  /* --------------------------------------------------------------------- */
  var SCREEN_WIDTH = 800;
  var SCREEN_HEIGHT = 600;
  var FPS = 60;
  var STEP_MS = 1000 / FPS;

  var COLORS = {
    white: '#ffffff',
    black: '#000000',
    red: '#ff0000',
    green: '#00ff00',
    blue: '#0000ff',
    gray: '#808080',
    road: '#505050',
    grass: '#228b22',
    yellow: '#ffff00',
    neonPink: '#ff00ff',
    neonCyan: '#00ffff',
  };

  var ROAD_WIDTH = 400;
  var ROAD_LEFT = (SCREEN_WIDTH - ROAD_WIDTH) / 2;
  var ROAD_RIGHT = ROAD_LEFT + ROAD_WIDTH;
  var LANE_COUNT = 3;
  var LANE_WIDTH = Math.floor(ROAD_WIDTH / LANE_COUNT);

  var PLAYER_WIDTH = 50;
  var PLAYER_HEIGHT = 80;
  var PLAYER_SPEED = 6.0;
  var PLAYER_MAX_SPEED = 14.0;
  var SCROLL_ACCEL = 0.15;
  var SCROLL_FRICTION = 0.985;
  var PLAYER_ACCEL = 0.45;
  var PLAYER_FRICTION = 0.96;
  var STARTING_LIVES = 3;
  var INVULNERABILITY_FRAMES = 120;

  var OBSTACLE_WIDTH = 50;
  var OBSTACLE_HEIGHT = 80;
  var OBSTACLE_BASE_SPEED = 4.0;
  var OBSTACLE_SPAWN_FRAMES = 90;
  var OBSTACLE_MIN_SPAWN_FRAMES = 45;

  var NITRO_DURATION_FRAMES = 180;
  var NITRO_SPEED_BOOST = 2.5;
  var NITRO_COOLDOWN_FRAMES = 300;
  var NITRO_SCROLL_ACCEL = 0.35;
  var NITRO_MAX_SCROLL_SPEED = 20.0;

  var SCORE_PER_DISTANCE = 0.1;
  var SCORE_NEAR_MISS = 50;
  var NEAR_MISS_DISTANCE = 40;

  var OBSTACLE_COLORS = [
    COLORS.red,
    COLORS.blue,
    COLORS.yellow,
    COLORS.neonPink,
    COLORS.green,
  ];

  var STATE_MENU = 'menu';
  var STATE_PLAYING = 'playing';
  var STATE_GAME_OVER = 'gameover';

  var HIGH_SCORE_KEY = 'tpr_high_score';

  /* --------------------------------------------------------------------- */
  /* Small helpers                                                          */
  /* --------------------------------------------------------------------- */
  function overlap(a, b) {
    return (
      a.x < b.x + b.w &&
      a.x + a.w > b.x &&
      a.y < b.y + b.h &&
      a.y + a.h > b.y
    );
  }

  function nearMiss(player, obstacle) {
    var horizontalClose =
      player.x + player.w > obstacle.x - NEAR_MISS_DISTANCE &&
      player.x < obstacle.x + obstacle.w + NEAR_MISS_DISTANCE;
    var verticalClose =
      Math.abs(player.y + player.h - obstacle.y) < NEAR_MISS_DISTANCE;
    return horizontalClose && verticalClose;
  }

  function loadHighScore() {
    try {
      var saved = parseInt(window.localStorage.getItem(HIGH_SCORE_KEY) || '0', 10);
      return isFinite(saved) ? Math.max(0, saved) : 0;
    } catch (err) {
      return 0;
    }
  }

  function saveHighScore(value) {
    try {
      window.localStorage.setItem(HIGH_SCORE_KEY, String(value));
    } catch (err) {
      /* storage disabled — never crash */
    }
  }

  /* --------------------------------------------------------------------- */
  /* Procedural audio (Web Audio equivalent of src/systems/audio.py)        */
  /* --------------------------------------------------------------------- */
  var MELODY = [
    [440.0, 150], [523.25, 150], [659.25, 150], [880.0, 150],
    [659.25, 150], [523.25, 150], [440.0, 150], [349.23, 150],
    [392.0, 150], [493.88, 150], [587.33, 150], [783.99, 150],
    [587.33, 150], [493.88, 150], [392.0, 150], [329.63, 150],
  ];

  function AudioManager() {
    this.ctx = null;
    this.musicBuffer = null;
    this.engineBuffer = null;
    this.crashBuffer = null;
    this.musicSource = null;
    this.engineSource = null;
    this.enabled = false;
  }

  AudioManager.prototype.ensure = function () {
    if (this.ctx || !(window.AudioContext || window.webkitAudioContext)) {
      return;
    }
    try {
      var Ctx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new Ctx();
      this.musicBuffer = this.buildMusic();
      this.engineBuffer = this.buildEngine();
      this.crashBuffer = this.buildCrash();
      this.enabled = true;
      this.startMusic();
    } catch (err) {
      this.enabled = false; /* degrade to silence */
    }
  };

  AudioManager.prototype.buildMusic = function () {
    var rate = this.ctx.sampleRate;
    var i;
    var total = 0;
    for (i = 0; i < MELODY.length; i += 1) {
      total += Math.floor((rate * MELODY[i][1]) / 1000);
    }
    var buffer = this.ctx.createBuffer(1, total, rate);
    var data = buffer.getChannelData(0);
    var volume = 0.2;
    var offset = 0;
    for (i = 0; i < MELODY.length; i += 1) {
      var freq = MELODY[i][0];
      var count = Math.floor((rate * MELODY[i][1]) / 1000);
      var step = (2 * Math.PI * freq) / rate;
      for (var n = 0; n < count; n += 1) {
        var envelope = 1 - (n / count) * 0.35;
        var wave = Math.sin(step * n) >= 0 ? 1 : -1;
        data[offset + n] = wave * envelope * volume;
      }
      offset += count;
    }
    return buffer;
  };

  AudioManager.prototype.buildEngine = function () {
    var rate = this.ctx.sampleRate;
    var buffer = this.ctx.createBuffer(1, rate, rate);
    var data = buffer.getChannelData(0);
    for (var i = 0; i < rate; i += 1) {
      var t = i / rate;
      data[i] =
        (0.7 * Math.sin(2 * Math.PI * 55.0 * t) +
          0.3 * Math.sin(2 * Math.PI * 110.0 * t)) *
        0.1;
    }
    return buffer;
  };

  AudioManager.prototype.buildCrash = function () {
    var rate = this.ctx.sampleRate;
    var count = Math.floor(rate * 0.45);
    var buffer = this.ctx.createBuffer(1, count, rate);
    var data = buffer.getChannelData(0);
    for (var i = 0; i < count; i += 1) {
      data[i] = (Math.random() * 2 - 1) * Math.exp((-6.0 * i) / count) * 0.55;
    }
    return buffer;
  };

  AudioManager.prototype.startMusic = function () {
    if (!this.enabled || this.musicSource) {
      return;
    }
    var source = this.ctx.createBufferSource();
    var gain = this.ctx.createGain();
    source.buffer = this.musicBuffer;
    source.loop = true;
    gain.gain.value = 0.35;
    source.connect(gain).connect(this.ctx.destination);
    source.start();
    this.musicSource = source;
  };

  AudioManager.prototype.startEngine = function () {
    if (!this.enabled || this.engineSource) {
      return;
    }
    var source = this.ctx.createBufferSource();
    var gain = this.ctx.createGain();
    source.buffer = this.engineBuffer;
    source.loop = true;
    gain.gain.value = 0.5;
    source.connect(gain).connect(this.ctx.destination);
    source.start();
    this.engineSource = source;
  };

  AudioManager.prototype.stopEngine = function () {
    if (this.engineSource) {
      try {
        this.engineSource.stop();
      } catch (err) {
        /* already stopped */
      }
      this.engineSource = null;
    }
  };

  AudioManager.prototype.playCrash = function () {
    if (!this.enabled) {
      return;
    }
    var source = this.ctx.createBufferSource();
    var gain = this.ctx.createGain();
    source.buffer = this.crashBuffer;
    gain.gain.value = 0.8;
    source.connect(gain).connect(this.ctx.destination);
    source.start();
  };

  /* --------------------------------------------------------------------- */
  /* Entities (mirrors car_race_game/src/entities/*.py)                     */
  /* --------------------------------------------------------------------- */
  function Player() {
    this.width = PLAYER_WIDTH;
    this.height = PLAYER_HEIGHT;
    this.x = Math.floor(SCREEN_WIDTH / 2 - this.width / 2);
    this.y = SCREEN_HEIGHT - this.height - 20;
    this.speedX = 0;
    this.lives = STARTING_LIVES;
    this.invulnerable = 0;
    this.nitroActive = 0;
    this.nitroCooldown = 0;
    this.color = COLORS.neonCyan;
  }

  Player.prototype.rect = function () {
    return {
      x: Math.round(this.x),
      y: Math.round(this.y),
      w: this.width,
      h: this.height,
    };
  };

  Player.prototype.update = function (keys) {
    if (keys.left) {
      this.speedX -= PLAYER_ACCEL;
    }
    if (keys.right) {
      this.speedX += PLAYER_ACCEL;
    }

    this.speedX *= PLAYER_FRICTION;

    var maxSpeed = PLAYER_SPEED;
    if (this.nitroActive > 0) {
      maxSpeed *= NITRO_SPEED_BOOST;
    }
    if (Math.abs(this.speedX) > maxSpeed) {
      this.speedX = this.speedX > 0 ? maxSpeed : -maxSpeed;
    }

    this.x += this.speedX;

    if (this.x < ROAD_LEFT) {
      this.x = ROAD_LEFT;
      this.speedX = 0;
    }
    if (this.x + this.width > ROAD_RIGHT) {
      this.x = ROAD_RIGHT - this.width;
      this.speedX = 0;
    }

    if (this.invulnerable > 0) {
      this.invulnerable -= 1;
    }
    if (this.nitroActive > 0) {
      this.nitroActive -= 1;
    }
    if (this.nitroCooldown > 0) {
      this.nitroCooldown -= 1;
    }
  };

  Player.prototype.activateNitro = function () {
    if (this.nitroCooldown === 0 && this.nitroActive === 0) {
      this.nitroActive = NITRO_DURATION_FRAMES;
      this.nitroCooldown = NITRO_COOLDOWN_FRAMES;
    }
  };

  Player.prototype.loseLife = function () {
    if (this.invulnerable > 0) {
      return false;
    }
    this.lives -= 1;
    this.invulnerable = INVULNERABILITY_FRAMES;
    this.speedX = 0;
    return this.lives <= 0;
  };

  Player.prototype.draw = function (ctx) {
    if (this.invulnerable > 0 && Math.floor(this.invulnerable / 4) % 2 === 0) {
      return;
    }
    drawCar(ctx, Math.round(this.x), Math.round(this.y), this.width, this.height, this.color);
  };

  function Obstacle(lane, speed) {
    this.width = OBSTACLE_WIDTH;
    this.height = OBSTACLE_HEIGHT;
    this.lane = lane;
    this.speed = speed;
    this.passed = false;

    var laneX = ROAD_LEFT + lane * LANE_WIDTH;
    this.x = laneX + Math.floor((LANE_WIDTH - this.width) / 2);
    this.y = -this.height;
    this.color = OBSTACLE_COLORS[Math.floor(Math.random() * OBSTACLE_COLORS.length)];
  }

  Obstacle.prototype.rect = function () {
    return {
      x: Math.round(this.x),
      y: Math.round(this.y),
      w: this.width,
      h: this.height,
    };
  };

  Obstacle.prototype.update = function (scrollSpeed) {
    this.y += this.speed + scrollSpeed * 0.5;
  };

  Obstacle.prototype.isOffScreen = function () {
    return this.y > SCREEN_HEIGHT;
  };

  Obstacle.prototype.draw = function (ctx) {
    drawCar(ctx, Math.round(this.x), Math.round(this.y), this.width, this.height, this.color);
  };

  function ObstacleManager() {
    this.obstacles = [];
    this.spawnTimer = 0;
  }

  ObstacleManager.prototype.spawn = function (scrollSpeed) {
    this.spawnTimer += 1;
    var spawnRate = Math.max(
      OBSTACLE_MIN_SPAWN_FRAMES,
      OBSTACLE_SPAWN_FRAMES - Math.floor(scrollSpeed * 6)
    );
    if (this.spawnTimer >= spawnRate) {
      var lane = Math.floor(Math.random() * LANE_COUNT);
      this.obstacles.push(new Obstacle(lane, OBSTACLE_BASE_SPEED));
      this.spawnTimer = 0;
    }
  };

  ObstacleManager.prototype.update = function (scrollSpeed) {
    var alive = [];
    for (var i = 0; i < this.obstacles.length; i += 1) {
      this.obstacles[i].update(scrollSpeed);
      if (!this.obstacles[i].isOffScreen()) {
        alive.push(this.obstacles[i]);
      }
    }
    this.obstacles = alive;
  };

  ObstacleManager.prototype.reset = function () {
    this.obstacles = [];
    this.spawnTimer = 0;
  };

  /* --------------------------------------------------------------------- */
  /* Rendering (mirrors car_race_game/src/systems/renderer.py)              */
  /* --------------------------------------------------------------------- */
  function drawCar(ctx, x, y, w, h, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x, y, w, h);
    ctx.fillStyle = COLORS.black;
    ctx.fillRect(x + 10, y + 15, w - 20, 20); /* cockpit */
    var wheelW = 8;
    var wheelH = 16;
    ctx.fillRect(x - 4, y + 10, wheelW, wheelH);
    ctx.fillRect(x + w - 4, y + 10, wheelW, wheelH);
    ctx.fillRect(x - 4, y + h - 26, wheelW, wheelH);
    ctx.fillRect(x + w - 4, y + h - 26, wheelW, wheelH);
  }

  function Renderer(ctx) {
    this.ctx = ctx;
    this.roadOffset = 0;
  }

  Renderer.prototype.drawRoad = function (scrollSpeed) {
    var ctx = this.ctx;
    this.roadOffset = (this.roadOffset + scrollSpeed) % 40;

    ctx.fillStyle = COLORS.grass;
    ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

    ctx.fillStyle = COLORS.road;
    ctx.fillRect(ROAD_LEFT, 0, ROAD_WIDTH, SCREEN_HEIGHT);

    ctx.fillStyle = COLORS.yellow;
    ctx.fillRect(ROAD_LEFT - 2, 0, 4, SCREEN_HEIGHT);
    ctx.fillRect(ROAD_RIGHT - 2, 0, 4, SCREEN_HEIGHT);

    var dashHeight = 40;
    var dashGap = 20;
    ctx.fillStyle = COLORS.white;
    for (var lane = 1; lane < LANE_COUNT; lane += 1) {
      var laneX = ROAD_LEFT + lane * LANE_WIDTH;
      var y = this.roadOffset;
      while (y < SCREEN_HEIGHT) {
        ctx.fillRect(laneX - 1, y, 3, dashHeight);
        y += dashHeight + dashGap;
      }
    }
  };

  Renderer.prototype.drawPlayer = function (player) {
    player.draw(this.ctx);
  };

  Renderer.prototype.drawObstacles = function (obstacles) {
    for (var i = 0; i < obstacles.length; i += 1) {
      obstacles[i].draw(this.ctx);
    }
  };

  Renderer.prototype.text = function (value, x, y, size, color, centered) {
    var ctx = this.ctx;
    ctx.font = 'bold ' + size + 'px "Segoe UI", Arial, sans-serif';
    ctx.textAlign = centered ? 'center' : 'left';
    ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = color;
    ctx.fillText(value, x, y);
  };

  Renderer.prototype.drawHud = function (score, lives, speed, nitroFrames) {
    this.text('Score: ' + score, 20, 42, 24, COLORS.white, false);
    this.text('Lives: ' + lives, 20, 72, 24, COLORS.white, false);
    this.text('Speed: ' + speed.toFixed(1), 20, 102, 24, COLORS.white, false);
    this.text(
      'Nitro: ' + (nitroFrames > 0 ? 'ACTIVE' : 'READY'),
      20,
      132,
      24,
      nitroFrames > 0 ? COLORS.neonCyan : COLORS.gray,
      false
    );
  };

  Renderer.prototype.drawMenu = function (highScore) {
    var cx = SCREEN_WIDTH / 2;
    this.text('TURBO PIXEL RACER', cx, 220, 60, COLORS.neonCyan, true);
    this.text('Dodge traffic. Survive. Score high.', cx, 275, 30, COLORS.white, true);
    this.text('High Score: ' + highScore, cx, 335, 24, COLORS.yellow, true);

    var controls = [
      'LEFT / RIGHT or A / D : Steer',
      'UP or W               : Accelerate',
      'SPACE                  : Nitro Boost',
    ];
    for (var i = 0; i < controls.length; i += 1) {
      this.text(controls[i], cx, 405 + i * 32, 22, COLORS.white, true);
    }

    this.text('Press ENTER to Start', cx, 530, 32, COLORS.green, true);
  };

  Renderer.prototype.drawGameOver = function (score, highScore) {
    var ctx = this.ctx;
    ctx.fillStyle = 'rgba(0, 0, 0, 0.725)';
    ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

    var cx = SCREEN_WIDTH / 2;
    this.text('GAME OVER', cx, 240, 64, COLORS.red, true);
    this.text('Final Score: ' + score, cx, 310, 32, COLORS.white, true);
    this.text('High Score: ' + highScore, cx, 360, 24, COLORS.yellow, true);
    this.text('Press ENTER to Restart', cx, 440, 32, COLORS.green, true);
    this.text('Press Q for Menu', cx, 490, 32, COLORS.red, true);
  };

  /* --------------------------------------------------------------------- */
  /* Game (mirrors car_race_game/src/game.py)                               */
  /* --------------------------------------------------------------------- */
  function Game(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.renderer = new Renderer(this.ctx);
    this.audio = new AudioManager();

    this.keys = { left: false, right: false, up: false };
    this.state = STATE_MENU;
    this.player = new Player();
    this.obstacleManager = new ObstacleManager();
    this.score = 0;
    this.bonusScore = 0;
    this.nearMisses = 0;
    this.highScore = loadHighScore();
    this.scrollSpeed = OBSTACLE_BASE_SPEED;
    this.distance = 0;
    this.scoreSubmitted = false;

    this.bindInput();
    this.resetRun(false);
    this.state = STATE_MENU;
  }

  Game.prototype.bindInput = function () {
    var self = this;

    window.addEventListener('keydown', function (event) {
      self.audio.ensure();

      switch (event.code) {
        case 'ArrowLeft':
        case 'KeyA':
          self.keys.left = true;
          event.preventDefault();
          break;
        case 'ArrowRight':
        case 'KeyD':
          self.keys.right = true;
          event.preventDefault();
          break;
        case 'ArrowUp':
        case 'KeyW':
          self.keys.up = true;
          event.preventDefault();
          break;
        case 'ArrowDown':
        case 'KeyS':
          event.preventDefault();
          break;
        case 'Space':
          if (self.state === STATE_PLAYING) {
            self.player.activateNitro();
          }
          event.preventDefault();
          break;
        case 'Enter':
          if (self.state === STATE_MENU || self.state === STATE_GAME_OVER) {
            self.startRun();
          }
          event.preventDefault();
          break;
        case 'KeyQ':
          if (self.state === STATE_GAME_OVER) {
            self.toMenu();
          }
          break;
        case 'Escape':
          if (self.state !== STATE_MENU) {
            self.toMenu();
          }
          break;
        default:
          break;
      }
    });

    window.addEventListener('keyup', function (event) {
      switch (event.code) {
        case 'ArrowLeft':
        case 'KeyA':
          self.keys.left = false;
          break;
        case 'ArrowRight':
        case 'KeyD':
          self.keys.right = false;
          break;
        case 'ArrowUp':
        case 'KeyW':
          self.keys.up = false;
          break;
        default:
          break;
      }
    });

    /* Tap the left/right half of the canvas to steer (phones). */
    this.canvas.addEventListener('pointerdown', function (event) {
      self.audio.ensure();
      if (self.state === STATE_MENU || self.state === STATE_GAME_OVER) {
        self.startRun();
        return;
      }
      var rect = self.canvas.getBoundingClientRect();
      var onLeft = event.clientX - rect.left < rect.width / 2;
      self.keys.left = onLeft;
      self.keys.right = !onLeft;
    });
    window.addEventListener('pointerup', function () {
      self.keys.left = false;
      self.keys.right = false;
    });
  };

  Game.prototype.resetRun = function (startAudio) {
    this.player = new Player();
    this.obstacleManager.reset();
    this.score = 0;
    this.bonusScore = 0;
    this.nearMisses = 0;
    this.distance = 0;
    this.scrollSpeed = OBSTACLE_BASE_SPEED;
    this.scoreSubmitted = false;
    if (startAudio) {
      this.audio.startEngine();
    }
  };

  Game.prototype.startRun = function () {
    this.resetRun(true);
    this.state = STATE_PLAYING;
    this.canvas.focus();
  };

  Game.prototype.toMenu = function () {
    this.audio.stopEngine();
    this.state = STATE_MENU;
  };

  Game.prototype.update = function () {
    if (this.state !== STATE_PLAYING) {
      return;
    }

    if (this.keys.up) {
      this.scrollSpeed = Math.min(this.scrollSpeed + SCROLL_ACCEL, PLAYER_MAX_SPEED);
    } else {
      this.scrollSpeed *= SCROLL_FRICTION;
    }

    if (this.player.nitroActive > 0) {
      this.scrollSpeed = Math.min(
        this.scrollSpeed + NITRO_SCROLL_ACCEL,
        NITRO_MAX_SCROLL_SPEED
      );
    }

    if (this.scrollSpeed < OBSTACLE_BASE_SPEED) {
      this.scrollSpeed = OBSTACLE_BASE_SPEED;
    }

    this.player.update(this.keys);

    this.obstacleManager.spawn(this.scrollSpeed);
    this.obstacleManager.update(this.scrollSpeed);

    this.distance += this.scrollSpeed * SCORE_PER_DISTANCE;
    this.score = Math.trunc(this.distance) + this.bonusScore;

    var i;
    var obstacle;
    if (this.player.invulnerable === 0) {
      for (i = 0; i < this.obstacleManager.obstacles.length; i += 1) {
        obstacle = this.obstacleManager.obstacles[i];
        if (overlap(this.player.rect(), obstacle.rect())) {
          var gameOver = this.player.loseLife();
          this.audio.playCrash();
          this.scrollSpeed = OBSTACLE_BASE_SPEED;
          if (gameOver) {
            this.endRun();
          }
          break;
        }
      }
    }

    if (this.state === STATE_PLAYING && this.player.invulnerable === 0) {
      for (i = 0; i < this.obstacleManager.obstacles.length; i += 1) {
        obstacle = this.obstacleManager.obstacles[i];
        if (!obstacle.passed && nearMiss(this.player.rect(), obstacle.rect())) {
          this.bonusScore += SCORE_NEAR_MISS;
          this.nearMisses += 1;
          this.score = Math.trunc(this.distance) + this.bonusScore;
          obstacle.passed = true;
          break;
        }
      }
    }
  };

  Game.prototype.endRun = function () {
    this.state = STATE_GAME_OVER;
    this.audio.stopEngine();
    if (this.score > this.highScore) {
      this.highScore = this.score;
      saveHighScore(this.highScore);
    }
    if (!this.scoreSubmitted) {
      this.scoreSubmitted = true;
      if (typeof window.roundOver === 'function') {
        window.roundOver({
          score: Math.max(0, Math.trunc(this.score)),
          distance: Math.max(0, Math.trunc(this.distance)),
          near_misses: Math.max(0, this.nearMisses),
        });
      }
    }
  };

  Game.prototype.draw = function () {
    if (this.state === STATE_MENU) {
      this.renderer.drawRoad(0);
      this.renderer.drawMenu(this.highScore);
      return;
    }

    if (this.state === STATE_PLAYING) {
      this.renderer.drawRoad(this.scrollSpeed);
      this.renderer.drawObstacles(this.obstacleManager.obstacles);
      this.renderer.drawPlayer(this.player);
      this.renderer.drawHud(
        this.score,
        this.player.lives,
        this.scrollSpeed,
        this.player.nitroActive
      );
      return;
    }

    /* game over */
    this.renderer.drawRoad(0);
    this.renderer.drawObstacles(this.obstacleManager.obstacles);
    this.renderer.drawPlayer(this.player);
    this.renderer.drawGameOver(this.score, this.highScore);
  };

  Game.prototype.run = function () {
    var self = this;
    var last = performance.now();
    var accumulator = 0;

    function frame(now) {
      accumulator += now - last;
      last = now;
      var steps = 0;
      while (accumulator >= STEP_MS && steps < 5) {
        self.update();
        accumulator -= STEP_MS;
        steps += 1;
      }
      if (accumulator > STEP_MS * 5) {
        accumulator = 0; /* tab was hidden — drop the backlog */
      }
      self.draw();
      window.requestAnimationFrame(frame);
    }

    window.requestAnimationFrame(frame);
  };

  /* --------------------------------------------------------------------- */
  /* Boot                                                                   */
  /* --------------------------------------------------------------------- */
  var canvas = document.getElementById('game');
  if (canvas) {
    var game = new Game(canvas);
    game.run();
    window.turboRace = game;
  }
})();





