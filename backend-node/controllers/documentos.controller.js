const documentosService = require("../services/documentos.service");

class DocumentosController {

    listar(req, res) {
        if (req.query.tipo) {
            return res.json(documentosService.obtenerPorTipo(req.query.tipo));
        }
        res.json(documentosService.obtenerTodos());
    }

    obtener(req, res) {
        try {
            res.json(documentosService.obtenerPorId(req.params.id));
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }

    crear(req, res) {
        try {
            const documento = documentosService.crear(req.body);
            res.status(201).json({ mensaje: "Documento registrado correctamente", documento });
        } catch (error) {
            res.status(400).json({ mensaje: error.message });
        }
    }

    eliminar(req, res) {
        try {
            documentosService.eliminar(req.params.id);
            res.json({ mensaje: "Documento eliminado" });
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }
}

module.exports = new DocumentosController();
