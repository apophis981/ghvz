'use strict';

class FakeBridge {
  constructor(idGenerator) {
    this.databaseOperations = [];
    this.unmappedDatabase = {};
    this.teeWriter = new TeeWriter();
    this.teeWriter.addDestination(new SimpleWriter(this.unmappedDatabase));
    var fakeServer = new FakeServer(idGenerator, this.teeWriter, new Date().getTime());
    var checkedServer = new CheckedServer(idGenerator, fakeServer, Bridge.METHODS_MAP);
    var cloningFakeSerer = new CloningWrapper(checkedServer, Bridge.METHODS);
    var delayingCloningFakeServer = new DelayingWrapper(cloningFakeSerer, Bridge.METHODS, 100);
    this.server = delayingCloningFakeServer;

    window.fakeBridge = this;

    for (const funcName of Bridge.METHODS) {
      if (!this[funcName])
        this[funcName] = (...args) => this.server[funcName](...args);
    }
  }
  signIn({userId}) {
    assert(userId);
    this.server.register({userId: userId});
    return userId;
  }
  getSignedInPromise({userId}) {
    assert(userId);
    return this.server.register({userId: userId}).then(() => userId);
  }
  listenToDatabase({destination}) {
    var gatedWriter = new GatedWriter(new MappingWriter(destination), false);
    var cloningWriter = new CloningWriter(gatedWriter);
    cloningWriter.batchedWrite([
      {
        type: 'set',
        path: ['games'],
        value: Utils.copyOf(this.unmappedDatabase.games),
      },
      {
        type: 'set',
        path: ['guns'],
        value: Utils.copyOf(this.unmappedDatabase.guns),
      },
      {
        type: 'set',
        path: ['users'],
        value: Utils.copyOf(this.unmappedDatabase.users),
      }
    ]);
    this.teeWriter.addDestination(cloningWriter);

    var interval =
        setInterval(() => {
          gatedWriter.openGate();
          gatedWriter.closeGate();
        }, 100);

    return () => {
      clearInterval(interval);
      this.teeWriter.removeDestination(cloningWriter);
    };
  }
  listenToGameAsAdmin(gameId) {
    // Do nothing. This method is really just an optimization.
  }
  listenToGameAsPlayer(gameId, playerId) {
    // Do nothing. This method is really just an optimization.
  }
  setPlayerId(playerId) {
    // Do nothing. This method was just for security.
  }
}

function CloningWrapper(inner, funcNames) {
  for (const funcName of funcNames) {
    this[funcName] = function(...args) {
      // console.log('Calling', funcName, 'with args', ...args);
      return Utils.copyOf(inner[funcName](...args.map(Utils.copyOf)));
    }
  }
}

function DelayingWrapper(inner, funcNames, delay) {
  delay = delay || 100;
  for (const funcName of funcNames) {
    this[funcName] = function(...args) {
      // console.log('Making request', funcName, ...args);
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          try {
            // console.log('Recipient received request', funcName, ...args);
            const result = inner[funcName](...args);
            // console.log('Recipient responding with', result);
            setTimeout(() => resolve(result), delay);
          } catch (error) {
            console.error(error);
            setTimeout(() => reject(error), delay);
          }
        }, delay);
      });
    };
  }
}
