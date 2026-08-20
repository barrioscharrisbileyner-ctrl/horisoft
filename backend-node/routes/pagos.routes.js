const express = require("express");
const router = express.Router();

const controller = require("../controllers/pagos.controller");

router.get("/", controller.listar);
router.post("/", controller.registrar);

module.exports = router;
