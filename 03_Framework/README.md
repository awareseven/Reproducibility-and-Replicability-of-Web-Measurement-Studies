# Run our measurement framework

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