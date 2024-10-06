import axios from 'axios';
import * as cheerio from 'cheerio';
import sqlite from 'sqlite3';
sqlite.verbose();

import {getLocToCountyLookupService} from '@fuzzysaj/location-to-usa-county';
const locToCounty = await getLocToCountyLookupService();

const START_YEAR = 1996;
const START_SEASON = 0;
const END_YEAR = 2024;
const END_SEASON = 1;

// spring–fall split is July 31 – Aug 1

const US_STATES_CODES = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"];

const MONARCH_TYPE_NAME = 'milkweed';
const SQLITE_PATH = `journeynorth_${MONARCH_TYPE_NAME}.db`;

function seasonIntToStr(seasonInt) {
    return ['spring','fall'][seasonInt];
}

async function query(year, seasonInt) {
    const seasonStr = seasonIntToStr(seasonInt);
    const url = `https://journeynorth.org/sightings/querylist.html?map=${MONARCH_TYPE_NAME}-${seasonStr}&year=${year}&season=${seasonStr}`;

    const responseHTML = (await axios.get(url)).data;
    // console.log(responseHTML);
    console.log(`fetched ${year} ${seasonStr}`);

    const $ = cheerio.load(responseHTML, { ignoreWhitespace: true });
    const $trs = $('#querylist tbody tr');
    // console.log($trs);

    const stmt = db.prepare("INSERT INTO sightings VALUES (?,?,?,?,?,?,?,?)");
    for (const $tr of $trs) {
        const $tds = $tr.children;
        const date = $($tds[1]).find('a').text().trim();
        const town = $($tds[2]).text().trim();
        const state = $($tds[3]).text().trim();
        if (!US_STATES_CODES.includes(state)) {
            continue;
        }

        const lat = parseFloat($($tds[4]).text().trim());
        const lng = parseFloat($($tds[5]).text().trim());
        const qtyRawStr = $($tds[6]).text().trim();
        const qty = qtyRawStr.length ? parseInt(qtyRawStr) : 1;

        let county, countyFIPS;
        try {
            const _c = await locToCounty(lat, lng);
            county = _c.county_name;
            countyFIPS = parseInt(_c.county_fips,10);
        } catch {
            // console.log(town);
        }
        if (county === null || (typeof county === 'string' && county.length === 0) || county === undefined || !county || isNaN(countyFIPS)) {
            continue;
        }

        stmt.run(date,town,state,lat,lng,qty,county,countyFIPS);
        // console.log(`inserted row`);
    }
    stmt.finalize();

    if (year < END_YEAR || (year === END_YEAR && seasonInt != END_SEASON)) {
        // next
        await query(...(seasonInt === 1 ? [year + 1,0] : [year,seasonInt + 1]));
    }
}

// const API_KEY = '38G3YQI6QMWSMQOPFX96PLDCFD9FA8XBK60Z4DR6DCAZT8KOUAUJ3DIC0J9EAPE2F8SZ8R6SN1GTDRLJ';
// const client = new scrapingbee.ScrapingBeeClient(API_KEY);

const db = new sqlite.Database('scrapers/JourneyNorth/' + SQLITE_PATH);
db.serialize(() => {
    db.run("CREATE TABLE sightings (date TEXT, town TEXT, state TEXT, lat REAL, lng REAL, qty INT, county TEXT, countyFIPS INT)");
});
console.log('created table');
await query(START_YEAR, START_SEASON);
db.close();