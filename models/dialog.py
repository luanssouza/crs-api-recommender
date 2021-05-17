import pandas as pd

class Dialog:
    """
    Dialog structure.

    Parameters
    ----------
    dialog_id : int
        Unique dialog id.
    user_id : int
        User identifier.
    g_zscore : dict
        Global zscore for the movies.
    subgraph : DataFrame
        DataFrame of dialog graph.
    edgelist : DataFrame
        DataFrame of graph edges.
    """

    def __init__(
        self, 
        dialog_id: int | None = None, 
        user_id: int | None = None,
        g_zscore: dict | None = None,
        subgraph: pd.DataFrame | None = None, 
        edgelist: pd.DataFrame | None = None
    ):

        # Calling superclass constructor
        super().__init__()

        # Identifiers
        self._dialog_id = dialog_id
        self._user_id = user_id

        # Graph properties
        self._edgelist = edgelist
        self._subgraph = subgraph

        # Dialog properties
        self._top = []
        self._watched = []
        self._dif_properties = []
        self._prefered_prop = []
        self._prefered_objects = []

        self._p_chosen = ""
        self._o_chosen = ""

        self._g_zscore = g_zscore

    # region Getters and Setters
    def set_p_chosen(self, p_chosen: str = None):
        """
        Update property selected.
        Parameters
        ----------
        p_chosen : str
            Property choosen.
        """
        self._p_chosen = p_chosen

    def get_p_chosen(self):
        """
        Gets object selected.
        Returns
        ----------
        p_chosen : str
            Object choosen.
        """
        return self._p_chosen
    
    def set_o_chosen(self, o_chosen: str = None):
        """
        Update object selected.
        Parameters
        ----------
        o_chosen : str
            Object choosen.
        """
        self._o_chosen = o_chosen

    def get_o_chosen(self):
        """
        Gets object selected.
        Returns
        ----------
        o_chosen : str
            Object choosen.
        """
        return self._o_chosen

    def set_subgraph(self, subgraph: pd.DataFrame | None = None):
        """
        Update reduced graph.
        Parameters
        ----------
        subgraph : DataFrame
            DataFrame of reduced graph.
        """
        self._subgraph = subgraph

    def get_subgraph(self):
        """
        Gets reduced graph.
        Returns
        ----------
        subgraph : DataFrame
            Reduced Graph.
        """
        return self._subgraph

    # endregion Getters and Setters

    def prefered_infos(self, prefered_prop: list | None = None, prefered_objects: list | None = None):
        """
        Setting prefered properties and objects.
        Parameters
        ----------
        prefered_properties : list 
            Prefered properties.
        prefered_objects : list 
            Prefered objects.
        """
        self._prefered_prop = prefered_prop
        self._prefered_objects = prefered_objects

    def dialog_infos(
        self,
        watched: list | None = None,
        edgelist: pd.DataFrame | None = None,
        prefered_prop: list | None = None,
        prefered_objects: list | None = None
    ):
        """
        Setting watched list, edgelist and prefered properties and objects.
        Parameters
        ----------
        watched : list
            List of watched movies.
        edgelist : DataFrame
            DataFrame of graph edges.
        prefered_properties : list 
            Prefered properties.
        prefered_objects : list 
            Prefered objects.
        """
        self._watched = watched
        self._edgelist = edgelist
        self.prefered_infos(prefered_prop, prefered_objects)
    
    def dialog_infos(self, top: pd.DataFrame | None = None, dif_properties: list | None = None):
        """
        Setting top of ordered movies and uniques properties.
        Parameters
        ----------
        top : DataFrame
            DataFrame of top of the ordered movies.
        dif_properties : list 
            List of uniques properties in the graph.
        """
        self._top = top
        self._dif_properties = dif_properties