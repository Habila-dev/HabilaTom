from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Transaction:
    """Modèle pour représenter une transaction financière"""
    
    id: str
    date: date
    type: str  # 'Entrée' ou 'Sortie'
    montant: float
    description: str
    categorie: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convertit la transaction en dictionnaire"""
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'type': self.type,
            'montant': self.montant,
            'description': self.description,
            'categorie': self.categorie or ''
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """Crée une transaction à partir d'un dictionnaire"""
        return cls(
            id=data['id'],
            date=date.fromisoformat(data['date']),
            type=data['type'],
            montant=float(data['montant']),
            description=data['description'],
            categorie=data.get('categorie', None)
        )
    
    def validate(self) -> bool:
        """Valide les données de la transaction"""
        if not self.id or not self.description:
            return False
        if self.type not in ['Entrée', 'Sortie']:
            return False
        if self.montant <= 0:
            return False
        return True
