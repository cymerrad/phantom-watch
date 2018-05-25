'use strict';

const puppeteer = require('puppeteer');
const _ = require('lodash');
const path = require('path');
const fs = require('fs');
const { URL } = require('url');
const uuidv4 = require('uuid/v4');

class JobWellDone {
  constructor(location, datetime) {
    this.location = location;
    this.datetime = datetime ? datetime : rfc3339();
  }
}

class JobFailed {
  constructor(link, error, datetime) {
    this.link = link;
    this.error = error;
    this.datetime = datetime ? datetime : rfc3339();
  }
}

class Dimensions {
  constructor(width, height) {
    this.width = width;
    this.height = height;
  }
}

let argv = require('minimist')(process.argv.slice(2));
const defaultExtension = ".png";
const defaultDimensions = new Dimensions(1366, 768);

/**
 * Return settings from argv
 */
async function getSettings() {
  let set = {
    output : argv.o ? argv.o : null,
    outputDir : argv.d ? argv.d : ".",
    dimensions : argv.s ? ((w,h)=>(new Dimensions(w,h)))(...argv.size.split(',')) : defaultDimensions,
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

/**
 * 
 * @param {puppeteer.Page} page 
 * @param {Number} curHeight 
 * @param {Number} downBy
 * @returns {[Number, Number]} New y position on the page and possible new height of the page
 */
async function scrollDown(page, curHeight, downBy) {
  // add
  let height = curHeight + downBy;

  // 'instant' in opposition to 'smooth'
  await page.evaluate(`window.scrollTo({top: ${height}, behavior: 'instant'})`);

  // wait for site's potential javascript to notice the change and do it's thing with css
  await (async() => new Promise(resolve => setTimeout(resolve, 200)))();

  // site's height might have changed
  let pageHeight = await page.evaluate('document.body.scrollHeight');

  return [height, pageHeight]
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
  try {
    await page.goto(`${pageUrl}`, {waitUntil: 'networkidle2'});
  } catch(e) {
    return [new JobFailed(pageUrl, "Resource failed to load", rfc3339())];
  }

  let out = path.parse(output);
  let dir = out.dir;
  let name = out.name;
  let ext = out.ext ? out.ext : defaultExtension;

  // TODO get rid of cookies nagbar or ads using h4x or some extension?

  // TODO
  if (!whole) {
    let batchDir = path.format({dir: dir, base: name});
    checkDirectorySync(batchDir);
    // screenshot the page pgDn by pgDn
    // dump many screenshots in 'dir/name/'
    let results = []
    let pageHeight = await page.evaluate('document.body.scrollHeight');
    let height = 0;
    while (height < pageHeight) {
      let screenshotFilename = path.format({dir: batchDir, name: `${height}-${pageHeight}`, ext: ext});
      try {
        await page.screenshot({path: screenshotFilename}); 
      } catch(e) {
        return [new JobFailed(pageUrl, "Saving "+`${screenshotFilename}`)]
      }
      let now = rfc3339();
      
      results.push(new JobWellDone(screenshotFilename, now));

      [height, pageHeight] = await scrollDown(page, height, dimensions.height);
    } 

    return results;
  } else {
    // scroll to the bottom of the page first - in case of dynamic, 'infinite' loading
    let pageHeight = await page.evaluate('document.body.scrollHeight');
    let height = 0;
    while (height < pageHeight) {
      [height, pageHeight] = await scrollDown(page, height, dimensions.height);
    }

    // Saving 
    let screenshotFilename = path.format({dir: dir, name: name, ext: ext});
    try {
      await page.screenshot({path: screenshotFilename, fullPage: true});
    } catch(e) {
      return [new JobFailed(pageUrl, "Saving "+`${screenshotFilename}`)]
    }
    let now = rfc3339();
    return [new JobWellDone(screenshotFilename, now)];
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
    return 1;
  }

  // username and password
  if (settings.password && settings.username) {
    // username and password provided, update every link
    pages = pages.map(p=>{p.username = settings.username; p.password = settings.password; return p;});
  } else if (settings.password || settings.username) {
    console.log("WARNING: password XOR username provided - ignoring due to insufficient credentials");
    return 1;
  }

  // output directory
  let outputDirectory = settings.outputDir;
  checkDirectorySync(outputDirectory);

  let whole = settings.wholePage;
  let dimensions = settings.dimensions;
  let results = [];

  // init browser
  const browser = await puppeteer.launch();

  // one explicitly named or all other cases
  if (pages.length == 1 && settings.output) {
    let name = path.parse(output).name;
    let extension = path.parse(output).ext ? path.parse(output).ext : defaultExtension;
    let outFull = path.format({
      dir: outputDirectory,
      name: name,
      ext: extension,
    });

    let finished = await screenshotPage(browser, pages[0], dimensions, outFull, whole);

    results.push(finished);
  } else {
    results = await Promise.all(
      pages.map(p=>screenshotPage(browser, p.href, dimensions, path.format({dir: outputDirectory, base: `${_.replace(p.hostname, /\./, '_')}_${rfc3339()}`}), whole))
    )
  }
  
  // kthxbai
  await browser.close();

  console.log(JSON.stringify(results));
  return 0;
})();
