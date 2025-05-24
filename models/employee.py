from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Employee:
    """Modèle pour représenter un employé"""
    
    id: str
    nom: str
    prenom: str
    poste: str
    salaire_mensuel: float
    date_embauche: date
    actif: bool = True
    
    def to_dict(self) -> dict:
        """Convertit l'employé en dictionnaire"""
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'poste': self.poste,
            'salaire_mensuel': self.salaire_mensuel,
            'date_embauche': self.date_embauche.strftime('%Y-%m-%d'),
            'actif': self.actif
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Employee':
        """Crée un employé à partir d'un dictionnaire"""
        return cls(
            id=data['id'],
            nom=data['nom'],
            prenom=data['prenom'],
            poste=data['poste'],
            salaire_mensuel=float(data['salaire_mensuel']),
            date_embauche=date.fromisoformat(data['date_embauche']),
            actif=bool(data.get('actif', True))
        )
    
    def nom_complet(self) -> str:
        """Retourne le nom complet de l'employé"""
        return f"{self.prenom} {self.nom}"
    
    def validate(self) -> bool:
        """Valide les données de l'employé"""
        if not self.id or not self.nom or not self.prenom:
            return False
        if self.salaire_mensuel <= 0:
            return False
        return True
