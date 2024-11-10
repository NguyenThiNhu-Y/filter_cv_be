from yacs.config import CfgNode as CN

def load_config(config_file):
    """
    Load a configuration file into a CfgNode.

    Args:
        config_file (str): Path to the YAML configuration file.

    Returns:
        CN: The loaded configuration as a CfgNode object.
    """
    cfg = CN()
    cfg.set_new_allowed(True)
    cfg.merge_from_file(config_file)
    return cfg

# Load individual configurations from YAML files
cfg_prompt = load_config("configs/prompt.yml")
cfg_db = load_config("configs/database.yml")
cfg_logger = load_config("configs/logger.yml")
cfg_file = load_config("configs/file.yml")

# Initialize the main configuration and allow new keys
cfg = CN()
cfg.set_new_allowed(True)

cfg.prompt = CN()
cfg.prompt.set_new_allowed(True)
cfg.prompt.merge_from_other_cfg(cfg_prompt)

cfg.db = CN()
cfg.db.set_new_allowed(True)
cfg.db.merge_from_other_cfg(cfg_db)

cfg.logger = CN()
cfg.logger.set_new_allowed(True)
cfg.logger.merge_from_other_cfg(cfg_logger)

cfg.file = CN()
cfg.file.set_new_allowed(True)
cfg.file.merge_from_other_cfg(cfg_file)