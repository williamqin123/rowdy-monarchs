import axios from 'axios';
import sqlite from 'sqlite3';
sqlite.verbose();

const key = 'silverosprey46';
const email = 'willqin123@gmail.com';
const param = '88101,81102,44201,42602,42401,42101,62101';
const YEAR_BEGIN = 1996;
const YEAR_END = 2024;

const STATES_LUT = {
    "01": "Alabama",
    "02": "Alaska",
    "04": "Arizona",
    "05": "Arkansas",
    "06": "California",
    "08": "Colorado",
    "09": "Connecticut",
    "10": "Delaware",
    "12": "Florida",
    "13": "Georgia",
    "15": "Hawaii",
    "16": "Idaho",
    "17": "Illinois",
    "18": "Indiana",
    "19": "Iowa",
    "20": "Kansas",
    "21": "Kentucky",
    "22": "Louisiana",
    "23": "Maine",
    "24": "Maryland",
    "25": "Massachusetts",
    "26": "Michigan",
    "27": "Minnesota",
    "28": "Mississippi",
    "29": "Missouri",
    "30": "Montana",
    "31": "Nebraska",
    "32": "Nevada",
    "33": "New Hampshire",
    "34": "New Jersey",
    "35": "New Mexico",
    "36": "New York",
    "37": "North Carolina",
    "38": "North Dakota",
    "39": "Ohio",
    "40": "Oklahoma",
    "41": "Oregon",
    "42": "Pennsylvania",
    "44": "Rhode Island",
    "45": "South Carolina",
    "46": "South Dakota",
    "47": "Tennessee",
    "48": "Texas",
    "49": "Utah",
    "50": "Vermont",
    "51": "Virginia",
    "53": "Washington",
    "54": "West Virginia",
    "55": "Wisconsin",
    "56": "Wyoming"
};

const SQLITE_PATH = `AirQualityEPA.db`;

async function getState1Year(stateNumber, year) {
    const bDate = year + '0101';
    const eDate = year + '0101';
    const url = `https://aqs.epa.gov/data/api/quarterlyData/byState?email=${email}&key=${key}&param=${param}&bdate=${bDate}&edate=${eDate}&state=${stateNumber}`;
    const responseJSON = (await axios.get(url)).data;
    console.log('fetched ' +  STATES_LUT[stateNumber]);
    // console.log(responseJSON);
    const entries = responseJSON['Data'];

    const stmt = db.prepare("INSERT INTO quarterlySummaries VALUES (?,?,?,?,?,?,?,?,?,?)");
    for (const entry of entries) {
        const year = entry['year'];
        const quarter = parseInt(entry['quarter']);
        const state = entry['state'];
        const county = entry['county'];
        const city = entry['city'];
        const arithmeticMeanValue = entry['arithmetic_mean'];
        const minimumValue = parseFloat(entry['minimum_value']);
        const maximumValue = parseFloat(entry['maximum_value']);
        const parameter = entry['parameter'];
        const unitsOfMeasure = entry['units_of_measure'];

        stmt.run(year,quarter,state,county,city,minimumValue,arithmeticMeanValue,maximumValue,parameter,unitsOfMeasure);
    }
    stmt.finalize();
}

async function getState(stateNumber) {
    for (var y = YEAR_BEGIN; y <= YEAR_END; y += 1) {
        await getState1Year(stateNumber, y);
    }
}

const db = new sqlite.Database('./AirQualityEPA/' + SQLITE_PATH);
db.serialize(() => {
    db.run("CREATE TABLE quarterlySummaries (year INT, quarter INT, state TEXT, county TEXT, city TEXT, minimumValue REAL, arithmeticMeanValue REAL, maximumValue REAL, parameter TEXT, unitsOfMeasure TEXT)");
});
console.log('created table');

for (const stateNumber of Object.keys(STATES_LUT)) {
    await getState(stateNumber);
}

db.close();
