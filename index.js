import express from 'express';
import { dirname } from 'path';
import { fileURLToPath } from 'url'
import path from 'path'
import bodyParser from 'body-parser'

const __dirname = dirname(fileURLToPath(import.meta.url));
const app = express();
const port = 3000;

app.use(express.static(path.join(__dirname, 'public')));

app.get("/", (req, res) => {
    res.sendFile(__dirname + '/public/index.html');
})

app.listen(port, () => {
    console.log(`Listening on ${port}`);
})