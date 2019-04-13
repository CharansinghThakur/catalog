# Item Catalog
### Project Overview
> The Item Catalog project consists of developing an application that provides a list of items, as well as provide a user registration and authentication system. This project uses persistent data storage to create a RESTful web application that allows users to perform Create, Read, Update, and Delete operations

### What Will I Learn?
  * Develop a RESTful web application using the Python framework Flask
  * Implementing third-party OAuth authentication.
  * Implementing CRUD (create, read, update and delete) operations.

## Skills used for this project
- Python
- HTML
- CSS
- Bootstrap
- Flask
- Jinja2
- SQLAchemy

#### PreRequisites
  * [Python ~2.7](https://www.python.org/)
  * [Vagrant](https://www.vagrantup.com/)
  * [VirtualBox](https://www.virtualbox.org/)
  
<!-- #### Setup Project:
  1. Install Vagrant and VirtualBox
  2. Download or Clone [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) repository.
  3. Find the catalog folder and replace it with the content of this current repository, by either downloading or cloning it from
  [Here](https://github.com/satheeshg/itemcatalog). -->

### How to Run
1. Install VirtualBox and Vagrant
2. Unzip and place the Item Catalog folder in your Vagrant directory
3. Launch Vagrant
```
$ Vagrant up 
```
4. Login to Vagrant
```
$ Vagrant ssh
```
5. Change directory to `/vagrant`
```
$ Cd /vagrant
```
6. Initialize the database
```
$ Python database_setup.py
```
7. Populate the database with some initial data
```
$ python defaultmenu.py
```
8. Launch application
```
$ Python guitars.py
```
9. Open the browser and go to http://localhost:5000

### JSON endpoints
#### Returns JSON of all States

```
/guitars/JSON
```



# catalog
# catalog
