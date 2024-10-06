# @fuzzysaj/location-to-usa-county

[![npm (scoped)](https://img.shields.io/npm/v/@fuzzysaj/location-to-usa-county.svg)](https://www.npmjs.com/package/@fuzzysaj/location-to-usa-county) [![Build Status](https://travis-ci.org/fuzzysaj/location-to-usa-county.svg?branch=master)](https://travis-ci.org/fuzzysaj/location-to-usa-county) [![dependencies Status](https://david-dm.org/fuzzysaj/location-to-usa-county/status.svg)](https://david-dm.org/fuzzysaj/location-to-usa-county) [![code coverage]( https://img.shields.io/codecov/c/github/fuzzysaj/location-to-usa-county.svg)](https://codecov.io/gh/fuzzysaj/location-to-usa-county)

A program to convert latitude/longitude coordinates into USA counties.  Data is stored locally based on publicly available boundary files from [United States Census Bureau](https://www.census.gov/programs-surveys/geography.html).

## Install

$ npm install @fuzzysaj/location-to-usa-county

## Usage

With JavaScript:

```js
const getLocToCountyLookupService = require('@fuzzysaj/location-to-usa-county');

(async ()=> {
  const locToCounty = await getLocToCountyLookupService(); 
  const county = await locToCounty(33.5038, -112.0253); // latitude, longitude for Phoenix
  // -> { county_name: "Maricopa", county_fips: "04013" }
})();
```

With TypeScript:

```ts
import { getLocToCountyLookupService, County } from '@fuzzysaj/location-to-usa-county'

(async ()=> {
  const locToCounty = await getLocToCountyLookupService();
  const county: County = await locToCounty(33.5038, -112.0253); // latitude, longitude for Phoeinx
  // -> { county_name: "Maricopa", county_fips: "04013" }
})();
```

## About
2018 US counties boundaries obtained from [United States Census Bureau](https://www.census.gov/programs-surveys/geography.html) in Shapefile format.  Shapefile was converted to GeoJson and downsampled to 10% of original size using [mapshaper](https://mapshaper.org/).