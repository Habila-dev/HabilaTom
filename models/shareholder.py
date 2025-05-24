from dataclasses import dataclass
from typing import Optional

@dataclass
class Shareholder:
    """Modèle pour représenter un actionnaire"""
    
    id: str
    nom: str
    prenom: str
    pourcentage_actions: float
    email: Optional[str] = None
    telephone: Optional[str] = None
    actif: bool = True
    
    def to_dict(self) -> dict:
        """Convertit l'actionnaire en dictionnaire"""
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'pourcentage_actions': self.pourcentage_actions,
            'email': self.email or '',
            'telephone': self.telephone or '',
            'actif': self.actif
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Shareholder':
        """Crée un actionnaire à partir d'un dictionnaire"""
        return cls(
            id=data['id'],
            nom=data['nom'],
            prenom=data['prenom'],
            pourcentage_actions=float(data['pourcentage_actions']),
            email=data.get('email', None) if data.get('email') else None,
            telephone=data.get('telephone', None) if data.get('telephone') else None,
            actif=bool(data.get('actif', True))
        )
    
    def nom_complet(self) -> str:
        """Retourne le nom complet de l'actionnaire"""
        return f"{self.prenom} {self.nom}"
    
    def validate(self) -> bool:
        """Valide les données de l'actionnaire"""
        if not self.id or not self.nom or not self.prenom:
            return False
        if self.pourcentage_actions <= 0 or self.pourcentage_actions > 100:
            return False
        return True
    
    def calculer_part_benefice(self, benefice_total: float) -> float:
        """Calcule la part de bénéfice pour cet actionnaire"""
        return benefice_total * (self.pourcentage_actions / 100)
