import { County, getLocToCountyLookupService } from '../src';
import 'mocha';
import { expect } from 'chai';

describe('location-to-usa-county', function() {

  describe('Basic county lookup', async function() {
    this.timeout(10000);

    const locToCounty = await getLocToCountyLookupService();

    it('When known Phoenix latitude, longitude is searched for, it finds the county', function() {
      const lat = 33.5038, lon = -112.0253; // Phoenix, USA
      const county: County = locToCounty(lat, lon);
      expect(county).to.not.be.null;
      expect(county.county_name).to.equal('Maricopa');
      expect(county.county_fips).to.equal('04013');
    });

    it('When known Anchorage latitude, longitude is searched for, it finds the county', function () {
      const lat = 61.177549, lon = -149.274354; // Anchorage, USA
      const county: County = locToCounty(lat, lon);
      expect(county).to.not.be.null;
      expect(county.county_name).to.equal('Anchorage');
      expect(county.county_fips).to.equal('02020');
    });

    it('When a non-USA location is searched for, it returns null', function() {
      const lat = 51.509865, lon = -0.118092; // London, England
      const county: County = locToCounty(lat, lon);
      expect(county).to.be.null;
    });

  });

});