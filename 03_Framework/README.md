# MultiCrawl (v0.1.0) 

This framework allows running web measurements with different crawling setups on different machines. So you can crawl websites almost in real-time with different setups (e.g., Firefox, Chrome, Firefox Headless). 

It currently supports Chrome and Firefox web browsers. In this version, the following main data types can be during the crawl collected:

- Cookies
- LocalStorage
- Requests
- Responses

Note that this is a mixed repository and contains files from [OpenWPM](https://github.com/openwpm/OpenWPM) (we utilize OpenWPM for running Firefox).  

The framework was developed for the study "[Reproducibility and Replicability of Web Measurement Studies](https://doi.org/10.1145/3485447.3512214)" published at the ACM Web Conference 2022. Check out our paper to see how different setup environments can affect your measurement. You can find on [this repository](https://github.com/awareseven/Reproducibility-and-Replicability-of-Web-Measurement-Studies) further material to the paper.


# How to configure & install the framework

1. Create a PostgreSQL database and run `/03_Framework/resources/posgres.sql` script.
2. Change the connection string for PostgreSQL in the `/DBOps.py` file.
3. Create an `authentication JSON` for Google Cloud API (see: https://cloud.google.com/docs/authentication/getting-started) and save it as `google.json` in the `/03_Framework/resources` folder.
4. Import your Tranco list to the table `sites` in PostgreSQL.
5. Run `/03_Framework/Commander_extract_Subpages.py` to extract subpages from imported Tranco list.
6. Create a dataset as `data` and the tables `requests`, `responses`, `cookies` and `localstorage` in your dataset - create columns for these tables as in ours `/02_data/public_data.md`.
7. Create a VM (Ubuntu 20.04)
8. Install requirements list in `/03_Framework/req.txt`.
9. Run `install.sh` to install OpenWPM.
10. Setup a VPN connection on the VM according to its configuration.
11. Create 24 VMs (Ubuntu 20.04), repeat steps `7-10`, or clone a VM.
12. Name each VM depending on your setup as in the function `getMode()` in `/03_Framework/setup.py`. 
13. Run `restart.sh` on each VM to run the measurement.