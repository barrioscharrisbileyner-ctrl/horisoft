const express = require("express");
const router = express.Router();

const controller = require("../controllers/pqr.controller");

router.get("/", controller.listar);
router.get("/:id", controller.obtener);
router.post("/", controller.crear);
router.put("/:id/respuesta", controller.responder);
router.put("/:id/estado", controller.cambiarEstado);
router.delete("/:id", controller.eliminar);

module.exports = router;
