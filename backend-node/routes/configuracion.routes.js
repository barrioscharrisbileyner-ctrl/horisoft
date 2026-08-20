const express = require("express");
const router = express.Router();

const controller = require("../controllers/configuracion.controller");

router.get("/", controller.listar);
router.get("/:clave", controller.obtener);
router.post("/", controller.crear);
router.put("/:clave", controller.actualizarValor);
router.delete("/:clave", controller.eliminar);

module.exports = router;
