const express = require("express");
const router = express.Router();

const controller = require("../controllers/visitantes.controller");

// GET    /visitantes              -> listar todos (o ?activas=true para filtrar)
// GET    /visitantes/:id          -> obtener un registro específico
// POST   /visitantes              -> registrar ingreso (aplica reglas de negocio)
// PUT    /visitantes/:id/salida   -> registrar salida
// DELETE /visitantes/:id          -> eliminar un registro

router.get("/", controller.listar);
router.get("/:id", controller.obtener);
router.post("/", controller.registrarIngreso);
router.put("/:id/salida", controller.registrarSalida);
router.delete("/:id", controller.eliminar);

module.exports = router;
