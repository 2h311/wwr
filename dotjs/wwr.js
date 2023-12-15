const fs = require("fs");
const path = require("path");
const axios = require("axios");
const cheerio = require("cheerio");

const wwrFeedLinks = {
  "All Other Remote Jobs":
    "https://weworkremotely.com/categories/all-other-remote-jobs.rss",
  "DevOps and Sysadmin Jobs":
    "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
  "Full-Stack Programming Jobs":
    "https://weworkremotely.com/categories/remote-full-stack-programming-jobs.rss",
  "Front-End Programming Jobs":
    "https://weworkremotely.com/categories/remote-front-end-programming-jobs.rss",
  "Back-End Programming Jobs":
    "https://weworkremotely.com/categories/remote-back-end-programming-jobs.rss",
};

const jobMapKeys = [
  "title",
  "region",
  "category",
  "type",
  "description",
  "pubDate",
  "expires_at",
  "link",
];

const getData = async (link) => {
  const response = await axios(link);
  if (response.status === 200 && response.statusText === "OK") {
    const data = await response.data;
    return data;
  }
  return "";
};

const getJobMap = (itemChildren) => {
  return jobMapKeys.reduce((accumulator, currentArrayValue) => {
    accumulator.set(
      currentArrayValue,
      itemChildren.children(currentArrayValue).text()
    );
    return accumulator;
  }, new Map());
};

const gatherAllJobs = async () => {
  const quiteBigArray = new Array();
  for (key in wwrFeedLinks) {
    const res = await getData(wwrFeedLinks[key]);
    const $ = await cheerio.load(res, {
      ignoreWhitespace: true,
      xmlMode: true,
    });

    const itemArray = new Array();
    $("item").map((_, item) => {
      const jobMap = getJobMap($(item));
      const convertedMap = Object.fromEntries(jobMap);
      itemArray.push(convertedMap);
      console.log(convertedMap);
    });

    const categoryToJobsMap = new Map();
    categoryToJobsMap.set(key, itemArray);
    const convertedMap = Object.fromEntries(categoryToJobsMap);
    quiteBigArray.push(convertedMap);
  }

  const outputFilename = path.join("jsons", `${new Date().toJSON()}.json`);
  fs.writeFile(outputFilename, JSON.stringify(quiteBigArray), (err) => {
    if (err) {
      console.error(err);
      return;
    }
    console.log("Successfully data written to the file!");
  });
};

gatherAllJobs();
