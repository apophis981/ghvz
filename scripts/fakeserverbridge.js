'use strict';

class FakeServerBridge {
  constructor() {
    this.rememberedEmail = null;
    this.rememberedCode = null;
    this.loggedInUserEmail = null;
  }
  delayed_(callbackThatReturnsAPromise) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        callbackThatReturnsAPromise().then(
            (value) => setTimeout(() => resolve(value), 100),
            (value) => setTimeout(() => reject(value), 100));
      }, 100);
    });
  }
  login(email, code) {
    return this.delayed_(() => {
      this.loggedInUserEmail = email;
      return Promise.resolve();
    });
  }
  sendLogInLink(email) {
    if (code == email + '123') {
      return this.delayed_(() => {
        this.loggedInUserEmail = email;
        return Promise.resolve();
      });
    } else {
      return this.delayed_(() => Promise.reject('Incorrect password'));
    }
  }
  addUser(email, initialCode) {
    return this.delayed_(() => {
      this.loggedInUserEmail = email;
      this.db.addUser(email);
    });
  }
  loginProtectedAndDelayed_(callbackThatReturnsAPromise) {
    if (this.loggedInUserEmail) {
      return this.delayed_(callbackThatReturnsAPromise);
    } else {
      return this.delayed_(() => Promise.reject('Not logged in'));
    }
  }
  findUser(email) {
    return this.loginProtectedAndDelayed_(() => {
      if (email == this.loggedInUserEmail) {
        return this.db.findUser(email)
      } else {
        return Promise.reject('Can only access your own user');
      }
    });
  }
}

class FakeDatabase {
  constructor() {
    this.usersByEmail = {};
    this.playersById = {};
    this.infections = [];
    this.gunsById = {};

    this.addUser('testuser@googlehvz.com');
  }
  addUser(email) {
    assert(!(email in this.usersByEmail));
    this.usersByEmail[email] = {
      email: email,
    };
  }
  findUser(email) {
    assert(email in this.usersByEmail);
    return this.usersByEmail[email];
  }
  addPlayer(playerId, name) {
    assert(!(playerId in this.playersById));
    this.playersById[playerId] = {
      id: playerId,
      name: name,
      revives: [],
    };
  }
  findPlayer(playerId) {
    assert(playerId in this.playersById);
    var player = this.playersById[playerId];
    var deaths = [];
    var kills = [];
    for (var i = 0; i < infections.length; i++) {
      if (infections[i].killerId == playerId) {
        deaths.push(infections[i]);
      }
      if (infections[i].victimId == playerId) {
        kills.push(infections[i]);
      }
    }
  }
  infectPlayer(killerId, victimId) {
    this.infections.push({
      time: new Date().getTime(),
      killerId: killerId,
      victimId: victimId,
    });
  }
  revivePlayer(playerId) {
    assert(playerId in this.playersById);
    var player = this.playersById[playerId];
    player.revives.push({
      time: new Date().getTime(),
    });
  }
  addGun(gunId) {
    assert(!(gunId in this.gunsById));
    this.gunsById[gunId] = {
      id: gunId,
      playerId: null,
    };
  }
  lendGun(gunId, playerId) {
    assert(gunId in this.gunsById);
    assert(playerId in this.playersById);
    var gun = this.gunsById[gunId];
    assert(gun.playerId == null);
    gun.playerId = playerId;
  }
  transferGun(gunId, fromplayerId, toplayerId) {
    assert(gunId in this.gunsById);
    assert(fromplayerId in this.playersById);
    assert(toplayerId in this.playersById);
    var gun = this.gunsById[gunId];
    assert(gun.playerId == fromplayerId);
    gun.playerId = toplayerId;
  }
  returnGun(gunId, playerId) {
    assert(gunId in this.gunsById);
    assert(playerId in this.playersById);
    var gun = this.gunsById[gunId];
    assert(gun.playerId == fromplayerId);
    gun.playerId = null;
  }
}
