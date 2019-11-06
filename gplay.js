const pup = require("puppeteer");
const fs = require("fs");

function delay(time) {
  return new Promise(function(resolve) {
    setTimeout(resolve, time);
  });
}

let proxies = JSON.parse(fs.readFileSync("formatted.json"));

async function get_charts(iso) {
  valid_proxies = proxies.filter(proxy => proxy.iso == iso);

  if (valid_proxies.length < 1) {
    console.log(`Couldn't find a proxy for ${iso}`);
    console.log("Skipping...");
    return null;
  } else {
    console.log(
      `Found ${valid_proxies.length} valid proxies located in ${iso}`
    );
  }
  /*
  formatted_valid_proxies = valid_proxies.map(
    proxy => `http://${proxy.user}:${proxy.pass}@${proxy.host}:${proxy.port}`
  );
    */
  proxy = valid_proxies[Math.floor(Math.random() * valid_proxies.length)];

  let browser = await pup.launch({
    headless: true,
    defaultViewport: { width: 1600, height: 1200 },
    args: [`--proxy-server=${proxy.host}:${proxy.port}`]
  });
  const page = await browser.newPage();
  await page.authenticate({
    username: proxy.user,
    password: proxy.pass
  });

  //await page.goto("https://ifconfig.co");
  //await delay(2000);

  top_charts = {
    top_apps: "Check out more content from Top Apps",
    top_free_apps: "Check out more content from Top Free Apps",
    top_paid_apps: "Check out more content from Paid Apps",
    top_selling_apps: "Check out more content from Top Selling Apps",
    top_grossing_apps: "Check out more content from Top Grossing Apps",
    top_games: "Check out more content from Top Games",
    top_free_games: "Check out more content from Top Free Games",
    top_paid_games: "Check out more content from Top Paid Games",
    top_selling_games: "Check out more content from Top Selling Games",
    top_grossing_games: "Check out more content from Top Grossing Games"
  };

  for (const k of Object.keys(top_charts)) {
    console.log(`Scraping ${k} for ${iso}`);
    var url = "https://play.google.com/store/apps/top";
    //var url = "https://ifconfig.co/";
    await page.goto(url, {
      waitUntil: "networkidle2"
    });

    //await delay(4000);
    const btn = await page.$(`[aria-label="${top_charts[k]}"]`);
    if (!btn) {
      console.log("skipped", k);
      continue;
    }

    await btn.click();

    await page.waitForSelector(".ImZGtf.mpg5gc");

    await page.evaluate(() => {
      location.reload(true);
    });

    await delay(2000);

    const bodyHandle = await page.$("body");

    const { height } = await bodyHandle.boundingBox();

    await bodyHandle.dispose();

    const viewportHeight = page.viewport().height;

    let viewportIncr = 0;

    var elements = await page.$$("div.Vpfmgd div.RZEgze");
    while (elements.length < 175) {
      await page.evaluate(_viewportHeight => {
        window.scrollBy(0, _viewportHeight);
      }, viewportHeight);
      await delay(2000);

      var elements = await page.$$("div.Vpfmgd div.RZEgze");
    }

    const re1 = /(?<=Rated\s)\d\.\d|\d/;
    var ranks = [];

    c = 1;
    for (const el of elements) {
      const link = await el.$eval("a", a => a.getAttribute("href"));

      const name = await el.$eval("div.WsMG1c.nnK0zc", title =>
        title.getAttribute("title")
      );

      try {
        var developer = await el.$eval("div.KoLSrc", dev => dev.textContent);
      } catch (err) {
        var developer = "";
      }
      const position = c;
      try {
        var rating = await el.$eval("div.pf5lIe > div[aria-label]", rating =>
          rating.getAttribute("aria-label")
        );
        var rating = parseFloat(rating.match(re1)[0]);
      } catch (err) {
        var rating = "";
      }
      try {
        var price = await el.$eval(
          ".VfPpfd.ZdBevf.i5DZme > span",
          price => price.textContent
        );
      } catch (err) {
        var price = 0;
      }

      ranks.push({
        link: "https://play.google.com/" + link,
        developer: developer,
        name: name,
        rank: position,
        rating: rating,
        price: price
      });
      //ranks.push({link:link, name:name, ranking:position, rating:})
      c += 1;
    }
    console.log(`Saving ${iso} - ${k}`);

    fs.writeFile(`${iso}_${k}.json`, JSON.stringify(ranks, null, 2), err =>
      console.log(err)
    );
  }

  await browser.close();
}

async function main() {
  if (process.argv.length < 3) {
    throw "Usage: node gplay.js US UK (...)";
  }
  var args = process.argv.slice(2, process.argv.length);
  console.log(args);
  for (const iso of args) {
    await get_charts(iso);
  }
}

main();
