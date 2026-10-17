/* start.ng glue: who's playing, the profile card, saving runs, the board.
 * Talks to the hidden https://start.ng/connect frame (see start.md).
 * The game itself never sees a password — start.ng owns sign-in. */
(function () {
  'use strict';

  var START_NG = 'https://start.ng';
  var API = 'https://api.start.ng';

  /* "turbo-race" on turbo-race.start.ng; sensible fallback elsewhere. */
  function gameName() {
    var first = location.hostname.split('.')[0];
    return first && /^[a-z0-9-]+$/.test(first) && first !== 'localhost'
      ? first
      : 'turbo-race';
  }
  var GAME = gameName();

  /* Drop a game session out of the address (we use the connect page). */
  (function cleanSession() {
    var params = new URLSearchParams(location.hash.slice(1));
    if (params.get('startng_session')) {
      history.replaceState(null, '', location.pathname + location.search);
    }
  })();

  var frame;

  function connectFrame() {
    if (!frame) {
      frame = new Promise(function (resolve, reject) {
        var el = document.createElement('iframe');
        el.hidden = true;
        el.src = START_NG + '/connect';
        el.onload = function () {
          resolve(el);
        };
        el.onerror = reject;
        document.body.append(el);
      });
    }
    return frame;
  }

  /* Send a message and wait for start.ng's reply (or null on timeout). */
  function askStartNg(message, replyType, timeoutMs) {
    return connectFrame().then(function (el) {
      return new Promise(function (resolve) {
        var requestId = Math.random().toString(36).slice(2);
        var timer = setTimeout(function () {
          done(null);
        }, timeoutMs || 5000);

        function done(reply) {
          clearTimeout(timer);
          window.removeEventListener('message', onMessage);
          resolve(reply);
        }

        function onMessage(event) {
          if (event.origin !== START_NG || event.source !== el.contentWindow) {
            return;
          }
          if (
            event.data &&
            event.data.type === replyType &&
            event.data.requestId === requestId
          ) {
            done(event.data);
          }
        }

        window.addEventListener('message', onMessage);
        el.contentWindow.postMessage(
          Object.assign({}, message, { requestId: requestId }),
          START_NG
        );
      });
    });
  }

  /* --------------------------------------------------------------------- */
  /* Profile card                                                           */
  /* --------------------------------------------------------------------- */
  var card = document.getElementById('player-card');
  var face = document.getElementById('player-face');
  var nameEl = document.getElementById('player-name');
  var accountEl = document.getElementById('player-account');
  var signIn = document.getElementById('player-sign-in');
  var messageEl = document.getElementById('message');
  var boardEl = document.getElementById('board');

  var signInUrl =
    START_NG +
    '/?return_to=' +
    encodeURIComponent(location.origin + location.pathname);

  if (signIn) {
    signIn.addEventListener('click', function () {
      location.href = signInUrl;
    });
  }

  var me = null;

  function showPlayer(reply) {
    if (!card) {
      return;
    }
    var user = reply && reply.user;
    var player = user || (reply && reply.guest) || { name: 'Guest' };
    me = user || null;

    if (face) {
      if (player.face) {
        face.src = player.face;
        face.hidden = false;
      } else {
        face.removeAttribute('src');
        face.hidden = true;
      }
    }
    if (nameEl) {
      nameEl.textContent = player.name || 'Guest';
    }
    if (accountEl) {
      accountEl.textContent =
        user && user.account ? '@' + user.account : 'Not signed in — playing as a guest';
    }
    if (signIn) {
      signIn.hidden = !!user;
    }
    card.hidden = false;
  }

  function showMessage(text, keepMs) {
    if (!messageEl) {
      return;
    }
    messageEl.textContent = text;
    messageEl.hidden = false;
    if (keepMs) {
      setTimeout(function () {
        messageEl.hidden = true;
      }, keepMs);
    }
  }

  function refreshWhoAmI() {
    return askStartNg({ type: 'startng:whoami' }, 'startng:user')
      .then(showPlayer)
      .catch(function () {
        showPlayer(null);
      });
  }

  /* --------------------------------------------------------------------- */
  /* Leaderboard                                                            */
  /* --------------------------------------------------------------------- */
  function statValue(entry, key) {
    if (entry.stats && typeof entry.stats[key] === 'number') {
      return entry.stats[key];
    }
    if (key === 'score' && typeof entry.score === 'number') {
      return entry.score;
    }
    return null;
  }

  function renderBoard(entries) {
    if (!boardEl) {
      return;
    }
    if (!entries || !entries.length) {
      var empty = document.createElement('li');
      empty.className = 'muted';
      empty.textContent = 'No runs yet — be the first on the board.';
      boardEl.replaceChildren(empty);
      return;
    }

    boardEl.replaceChildren(
      ...entries.map(function (entry) {
        var li = document.createElement('li');
        if (me && entry.player_id === me.id) {
          li.className = 'me';
        }
        var who = document.createElement('span');
        who.textContent = '#' + entry.rank + ' ' + entry.name + ' ';
        var cols = document.createElement('span');
        cols.className = 'cols';
        var parts = [];
        var score = statValue(entry, 'score');
        var distance = statValue(entry, 'distance');
        var nearMisses = statValue(entry, 'near_misses');
        if (score !== null) {
          parts.push(score + ' pts');
        }
        if (distance !== null) {
          parts.push('dist ' + distance);
        }
        if (nearMisses !== null) {
          parts.push(nearMisses + ' near misses');
        }
        cols.textContent = parts.join(' · ');
        li.append(who, cols);
        return li;
      })
    );
  }

  /* Public GET — works for guests, and when the connect frame is absent
   * (for example when the page is opened outside *.start.ng). */
  function fetchBoardOverHttp() {
    return fetch(API + '/games/' + GAME + '/leaderboard?limit=10')
      .then(function (res) {
        return res.ok ? res.json() : [];
      })
      .then(renderBoard)
      .catch(function () {
        if (boardEl) {
          var li = document.createElement('li');
          li.className = 'muted';
          li.textContent = 'Leaderboard unavailable right now.';
          boardEl.replaceChildren(li);
        }
      });
  }

  function refreshLeaderboard() {
    askStartNg({ type: 'startng:leaderboard', limit: 10 }, 'startng:leaderboardData')
      .then(function (reply) {
        if (reply && reply.ok) {
          renderBoard(reply.entries);
          return;
        }
        return fetchBoardOverHttp();
      })
      .catch(fetchBoardOverHttp);
  }

  /* --------------------------------------------------------------------- */
  /* Saving a run — called by the game with startng.json stats              */
  /* --------------------------------------------------------------------- */
  window.roundOver = function (stats) {
    askStartNg({ type: 'startng:score', stats: stats }, 'startng:scoreSaved')
      .then(function (reply) {
        if (!reply) {
          fetchBoardOverHttp();
          return;
        }
        if (reply.ok && reply.result) {
          showMessage(
            reply.result.improved
              ? "New best! You're #" + reply.result.rank
              : 'Not your best this time (#' + reply.result.rank + ')',
            6000
          );
        } else {
          showMessage(reply.error || 'Sign in to save your score', 6000);
        }
        refreshLeaderboard();
      })
      .catch(function () {
        fetchBoardOverHttp();
      });
  };

  /* Ask again when the player comes back — they may have signed in/out. */
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden) {
      refreshWhoAmI();
    }
  });
  window.addEventListener('focus', refreshWhoAmI);

  refreshWhoAmI();
  refreshLeaderboard();
})();


