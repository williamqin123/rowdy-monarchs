import { gzToJson } from '../src/file-utils';
import * as path from 'path';
import 'mocha';
import { expect } from 'chai';

describe('file-utils', function() {

  describe('Load and parse JSON from a text file.', function() {
    it('When a JSON text file is specified, it is loaded and parsed into an object.', async function() {
      const filePath = path.join(__dirname, '../data/facts.json.gz');
      const facts = await gzToJson(filePath);
      expect(facts).to.not.be.null;
      expect(typeof facts).to.equal('object');
      expect(facts.dictionary[0].word).to.equal('apple');
    });

  });

});