'use strict';

const puppeteer = require('puppeteer');
const _ = require('lodash');
const path = require('path');
const fs = require('fs');
const { URL } = require('url');
const uuidv4 = require('uuid/v4');

let argv = require('minimist')(process.argv.slice(2));

/**
 * Return settings from argv
 */
async function getSettings() {
  let set = {
    output : argv.o ? argv.o : null,
    outputDir : argv.d ? argv.d : ".",
    dimensions : argv.s ? ((w,h)=>(new Dimensions(w,h)))(...argv.size.split(',')) : new Dimensions(1366, 768),
    username : argv.u ? argv.u : null,
    password : argv.p ? argv.p : null,
    wholePage : argv.whole ? true : false,
    tryToGetClearView : argv.clear ? true : false,
    pages : (argv._.length > 0) ? argv._ : (()=>{throw "no pages to screenshot"}),
  }
  return set;
}

/**
 * Return current datetime in RFC3339 format.
 * @return {!String}
 */
function rfc3339() {
  let date = new Date();
  let [H, M, s] = [_.padStart(date.getHours(), 2, '0'), _.padStart(date.getMinutes(), 2, '0'), _.padStart(date.getSeconds(), 2, '0')];
  let [d, m, y] = [_.padStart(date.getDay(), 2, '0'), _.padStart(date.getMonth(), 2, '0'), date.getFullYear().toString()];
  return `${y}-${m}-${d}T${H}:${M}:${s}`;
}

/**
 * 
 * @param {!String} directory 
 */
function checkDirectorySync(directory) {  
  try {
    fs.statSync(directory);
  } catch(e) {
    fs.mkdirSync(directory);
  }
}

class Dimensions {
  constructor(width, height) {
    this.width = width;
    this.height = height;
  }
}

/**
 * 
 * @param {puppeteer.Browser} browser 
 * @param {URL} pageUrl 
 * @param {Dimensions} dimensions 
 * @param {String} output 
 * @param {Boolean} whole 
 */
async function screenshotPage(browser, pageUrl, dimensions, output, whole) {
  const page = await browser.newPage();
  await page.setViewport(dimensions);
  await page.goto(`${pageUrl}`, {waitUntil: 'networkidle2'});

  let out = path.parse(output);
  let dir = out.dir;
  let name = out.name;
  let ext = out.ext ? out.ext : ".png";

  // TODO get rid of cookies nagbar or ads using h4x or some extension?

  // TODO
  if (!whole) {
    // screenshot the page pgDn by pgDn
    // dump many screenshots in 'dir/name/'

    return []
  } else {
    // Saving 
    let now = rfc3339();
    let file = path.format({dir: dir, name: name, ext: ext})
    console.log(`Saving to ${file}`);
    await page.screenshot({path: file});
    return [new JobWellDone(file, now)];
  }
}

class JobWellDone {
  constructor(location,datetime) {
    this.location = location;
    this.datetime = datetime;
  }
}

// main 
(async() => {
  var settings = await getSettings();
  
  // parse pages
  try {
    var pages = settings.pages.map(p=>{try {return new URL(p)} catch (e) {console.log("invalid url:", p); return null;} });
  } catch (e) {}
  pages = pages.filter(x => x);
  if (pages.length == 0) {
    console.log("nothing to process");
    return;
  }

  // username and password
  if (settings.password && settings.username) {
    // username and password provided, update every link
    pages = pages.map(p=>{p.username = settings.username; p.password = settings.password; return p;});
  } else if (settings.password || settings.username) {
    console.log("WARNING: password XOR username provided - ignoring due to insufficient credentials");
  }

  // output directory
  let outputDirectory = settings.outputDir;
  checkDirectorySync(outputDirectory);

  let dimensions = settings.dimensions;
  let results = [];

  // init browser
  const browser = await puppeteer.launch();

  // one or many
  if (pages.length == 1 && settings.output) {
    let name = path.parse(output).name;
    let extension = path.parse(output).ext ? path.parse(output).ext : ".png"
    let outFull = path.format({
      dir: outputDirectory,
      name: name,
      ext: extension,
    });

    let finished = await screenshotPage(browser, pages[0], dimensions, outFull, true);

    results.push(finished);
  } else {
    results = await Promise.all(
      pages.map(p=>screenshotPage(browser, p.href, dimensions, uuidv4(), true))
    )
  }
  
  // kthxbai
  await browser.close();

  return results;
})();
